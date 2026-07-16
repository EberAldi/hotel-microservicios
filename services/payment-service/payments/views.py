from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Pago, Factura, Reembolso
from .serializers import PagoSerializer, FacturaSerializer, ReembolsoSerializer
from common.permissions import EsDuenoPagoOAdmin, EsDuenoFacturaOAdmin, EsDuenoReembolsoOVerAdmin
from common.reservation_client import verificar_reservacion, verificar_carrito


def _siguiente_numero_factura():
    ultima = Factura.objects.order_by('-numero_factura').first()
    siguiente = (int(ultima.numero_factura.split('-')[1]) + 1) if ultima else 1
    return f"FAC-{siguiente:05d}"


class PagoViewSet(viewsets.ModelViewSet):
    """
    cliente: solo ve/gestiona SUS pagos. admin: ve y gestiona todos.
    Al crear, se verifica en vivo contra reservation-service que la
    reservacion o el carrito indicado exista y le pertenezca al cliente.

    IMPORTANTE: 'estado' es read-only en el serializer -- no se puede
    cambiar con PUT/PATCH normal (evita que un cliente se auto-declare
    su pago como exitoso). Para confirmar un pago, usar el endpoint
    /pagos/{id}/confirmar/, que ademas genera la Factura automaticamente.
    """
    serializer_class = PagoSerializer
    permission_classes = [EsDuenoPagoOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Pago.objects.all().order_by('-id')
        if usuario.rol == 'cliente':
            queryset = queryset.filter(cliente_id=usuario.cliente_id)
            return queryset
        reservacion_id = self.request.query_params.get('reservacion_id')
        carrito_id = self.request.query_params.get('carrito_id')
        estado = self.request.query_params.get('estado')
        if reservacion_id:
            queryset = queryset.filter(reservacion_id=reservacion_id)
        if carrito_id:
            queryset = queryset.filter(carrito_id=carrito_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        auth_header = self.request.META.get('HTTP_AUTHORIZATION')

        reservacion_id = serializer.validated_data.get('reservacion_id')
        carrito_id = serializer.validated_data.get('carrito_id')

        if reservacion_id:
            verificar_reservacion(reservacion_id, auth_header)
        else:
            verificar_carrito(carrito_id, auth_header)

        cliente_id = usuario.cliente_id if usuario.rol == 'cliente' else self.request.data.get('cliente_id')
        if not cliente_id:
            raise PermissionDenied('Como admin, debes indicar cliente_id en el body.')
        serializer.save(cliente_id=cliente_id)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Pago modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Pago modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Pago eliminado correctamente'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='confirmar')
    def confirmar(self, request, pk=None):
        """
        POST /api/pagos/pagos/{id}/confirmar/
        Marca el pago como 'exitoso' y genera su Factura automaticamente.
        Es la UNICA forma legitima de pasar un pago a 'exitoso'.
        """
        pago = self.get_object()
        if pago.estado == 'exitoso':
            return Response({'detail': 'Este pago ya esta confirmado.'}, status=400)

        id_transaccion = request.data.get('id_transaccion', '')
        pago.estado = 'exitoso'
        if id_transaccion:
            pago.id_transaccion = id_transaccion
        pago.save(update_fields=['estado', 'id_transaccion'])

        if not hasattr(pago, 'factura'):
            Factura.objects.create(pago=pago, numero_factura=_siguiente_numero_factura())

        return Response({
            'mensaje': 'Pago confirmado correctamente',
            'numero_factura': pago.factura.numero_factura,
        }, status=200)

    @action(detail=True, methods=['post'], url_path='marcar-fallido')
    def marcar_fallido(self, request, pk=None):
        """POST /api/pagos/pagos/{id}/marcar-fallido/"""
        pago = self.get_object()
        if pago.estado == 'exitoso':
            return Response({'detail': 'No se puede marcar como fallido un pago ya exitoso.'}, status=400)
        pago.estado = 'fallido'
        pago.save(update_fields=['estado'])
        return Response({'mensaje': 'Pago marcado como fallido'}, status=200)


class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura -- las facturas se generan automaticamente al confirmar un pago."""
    serializer_class = FacturaSerializer
    permission_classes = [EsDuenoFacturaOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Factura.objects.select_related('pago').all()
        if usuario.rol == 'cliente':
            queryset = queryset.filter(pago__cliente_id=usuario.cliente_id)
        return queryset


class ReembolsoViewSet(viewsets.ModelViewSet):
    """
    cliente: crea solicitudes de reembolso sobre SUS pagos (siempre queda
    en 'pendiente', no puede auto-aprobarse). admin: aprueba/rechaza.
    """
    serializer_class = ReembolsoSerializer
    permission_classes = [EsDuenoReembolsoOVerAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Reembolso.objects.select_related('pago').all().order_by('-creado_en')
        if usuario.rol == 'cliente':
            queryset = queryset.filter(pago__cliente_id=usuario.cliente_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        pago = serializer.validated_data.get('pago')
        if usuario.rol == 'cliente' and str(pago.cliente_id) != str(usuario.cliente_id):
            raise PermissionDenied('No puedes solicitar un reembolso de un pago que no es tuyo.')
        serializer.save(estado='pendiente')

    def update(self, request, *args, **kwargs):
        if request.user.rol != 'admin':
            raise PermissionDenied('Solo un admin puede aprobar o rechazar un reembolso.')
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Reembolso modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.rol != 'admin':
            raise PermissionDenied('Solo un admin puede eliminar un reembolso.')
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reembolso eliminado correctamente'}, status=status.HTTP_200_OK)