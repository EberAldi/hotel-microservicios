from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Reservacion, ReservacionServicio, HistorialEstadoReservacion, Carrito, CarritoItem
from .serializers import (
    ReservacionSerializer, ReservacionServicioSerializer,
    HistorialEstadoReservacionSerializer, CarritoSerializer, CarritoItemSerializer,
)
from common.permissions import (
    EsClienteOAdmin, EsDuenoReservacionOAdmin, EsDuenoReservacionServicioOAdmin,
    EsDuenoCarritoOAdmin, EsDuenoCarritoItemOAdmin,
)
from common.catalog_client import obtener_servicio


class ReservacionViewSet(viewsets.ModelViewSet):
    """
    cliente: solo ve/modifica/cancela SUS reservaciones. admin: ve y
    gestiona todas. Cada cambio de 'estado' se registra automaticamente
    en historial_estados_reservacion.
    """
    serializer_class = ReservacionSerializer
    permission_classes = [EsDuenoReservacionOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Reservacion.objects.all().order_by('-fecha_entrada')
        if usuario.rol == 'cliente':
            return queryset.filter(cliente_id=usuario.cliente_id)
        cliente_id = self.request.query_params.get('cliente_id')
        estado = self.request.query_params.get('estado')
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.rol == 'cliente':
            reservacion = serializer.save(cliente_id=usuario.cliente_id)
        else:
            cliente_id = self.request.data.get('cliente_id')
            if not cliente_id:
                raise PermissionDenied('Como admin, debes indicar cliente_id en el body.')
            reservacion = serializer.save(cliente_id=cliente_id)
        HistorialEstadoReservacion.objects.create(
            reservacion=reservacion, estado_anterior='', estado_nuevo=reservacion.estado,
            motivo='Reservacion creada'
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        estado_anterior = instance.estado
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        reservacion = serializer.save()
        if reservacion.estado != estado_anterior:
            HistorialEstadoReservacion.objects.create(
                reservacion=reservacion, estado_anterior=estado_anterior, estado_nuevo=reservacion.estado,
                motivo=request.data.get('motivo', '')
            )
        return Response({'mensaje': 'Reservación modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reservación eliminada correctamente'}, status=status.HTTP_200_OK)


class ReservacionServicioViewSet(viewsets.ModelViewSet):
    """
    Agrega servicios a una reservacion. El precio_unitario NUNCA lo manda
    el cliente: se consulta en vivo a catalog-service al crear el item.
    """
    serializer_class = ReservacionServicioSerializer
    permission_classes = [EsDuenoReservacionServicioOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = ReservacionServicio.objects.select_related('reservacion').all()
        if usuario.rol == 'cliente':
            queryset = queryset.filter(reservacion__cliente_id=usuario.cliente_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        reservacion = serializer.validated_data.get('reservacion')
        if usuario.rol == 'cliente' and str(reservacion.cliente_id) != str(usuario.cliente_id):
            raise PermissionDenied('No puedes agregar servicios a una reservación que no es tuya.')

        servicio_id = serializer.validated_data.get('servicio_id')
        datos_servicio = obtener_servicio(servicio_id)
        serializer.save(precio_unitario=Decimal(datos_servicio['precio']))

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación eliminado correctamente'}, status=status.HTTP_200_OK)


class HistorialEstadoReservacionViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura. cliente ve el historial de SUS reservaciones, admin ve todo."""
    serializer_class = HistorialEstadoReservacionSerializer
    permission_classes = [EsClienteOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = HistorialEstadoReservacion.objects.select_related('reservacion').all()
        if usuario.rol == 'cliente':
            queryset = queryset.filter(reservacion__cliente_id=usuario.cliente_id)
        reservacion_id = self.request.query_params.get('reservacion_id')
        if reservacion_id:
            queryset = queryset.filter(reservacion_id=reservacion_id)
        return queryset


class CarritoViewSet(viewsets.ModelViewSet):
    """
    Carrito de servicios sueltos, sin reservacion. cliente ve/gestiona el
    suyo, admin ve todos. No se permite mas de un carrito 'activo' a la vez
    por cliente.
    """
    serializer_class = CarritoSerializer
    permission_classes = [EsDuenoCarritoOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Carrito.objects.all().order_by('-creado_en')
        if usuario.rol == 'cliente':
            return queryset.filter(cliente_id=usuario.cliente_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        cliente_id = usuario.cliente_id if usuario.rol == 'cliente' else self.request.data.get('cliente_id')
        if not cliente_id:
            raise PermissionDenied('Como admin, debes indicar cliente_id en el body.')
        if Carrito.objects.filter(cliente_id=cliente_id, estado='activo').exists():
            raise ValidationError('Ya existe un carrito activo para este cliente.')
        serializer.save(cliente_id=cliente_id)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Carrito modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Carrito modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Carrito eliminado correctamente'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='checkout')
    def checkout(self, request, pk=None):
        """
        POST /api/reservaciones/carritos/{id}/checkout/
        Marca el carrito 'pendiente_pago', listo para que payment-service
        lo cobre (esa conexion se construye cuando toquemos payment-service).
        """
        carrito = self.get_object()
        if carrito.estado != 'activo':
            return Response({'detail': 'Solo se puede hacer checkout de un carrito activo.'}, status=400)
        if not carrito.items.exists():
            return Response({'detail': 'El carrito esta vacio.'}, status=400)
        carrito.estado = 'pendiente_pago'
        carrito.save(update_fields=['estado'])
        return Response({'mensaje': 'Carrito listo para pago', 'carrito_id': str(carrito.id)}, status=200)


class CarritoItemViewSet(viewsets.ModelViewSet):
    """
    Items del carrito. El precio_unitario_snapshot NUNCA lo manda el
    cliente: se consulta en vivo a catalog-service. Solo se puede
    agregar/quitar items mientras el carrito este 'activo'.
    """
    serializer_class = CarritoItemSerializer
    permission_classes = [EsDuenoCarritoItemOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = CarritoItem.objects.select_related('carrito').all()
        if usuario.rol == 'cliente':
            queryset = queryset.filter(carrito__cliente_id=usuario.cliente_id)
        carrito_id = self.request.query_params.get('carrito_id')
        if carrito_id:
            queryset = queryset.filter(carrito_id=carrito_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        carrito = serializer.validated_data.get('carrito')
        if usuario.rol == 'cliente' and str(carrito.cliente_id) != str(usuario.cliente_id):
            raise PermissionDenied('No puedes agregar items a un carrito que no es tuyo.')
        if carrito.estado != 'activo':
            raise ValidationError('Solo se pueden agregar items a un carrito activo.')

        servicio_id = serializer.validated_data.get('servicio_id')
        datos_servicio = obtener_servicio(servicio_id)
        serializer.save(precio_unitario_snapshot=Decimal(datos_servicio['precio']))

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Ítem de carrito modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Ítem de carrito modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Ítem de carrito eliminado correctamente'}, status=status.HTTP_200_OK)