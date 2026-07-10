from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Reservacion, ReservacionServicio
from .serializers import ReservacionSerializer, ReservacionServicioSerializer
from common.permissions import EsDuenoReservacionOAdmin, EsDuenoReservacionServicioOAdmin


class ReservacionViewSet(viewsets.ModelViewSet):
    """
    Requiere JWT con rol 'cliente' o 'admin'.
    - cliente: solo ve/modifica/cancela SUS PROPIAS reservaciones.
    - admin: ve y gestiona todas.

    Filtros opcionales por query param (solo tienen efecto para admin,
    un cliente siempre ve nada mas las suyas):
      /api/reservaciones/reservaciones/?cliente_id=<uuid>
      /api/reservaciones/reservaciones/?estado=draft
    """
    serializer_class = ReservacionSerializer
    permission_classes = [EsDuenoReservacionOAdmin]

    def get_queryset(self):
        usuario = self.request.user
        queryset = Reservacion.objects.all().order_by('-fecha_entrada')
        if usuario.rol == 'cliente':
            queryset = queryset.filter(cliente_id=usuario.cliente_id)
            return queryset
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
            serializer.save(cliente_id=usuario.cliente_id)
        else:
            # admin creando a nombre de otro cliente: debe mandar cliente_id
            # explicito en el body (no esta en read_only_fields para admin,
            # pero como el serializer es compartido, aqui lo tomamos del
            # request.data directo)
            cliente_id = self.request.data.get('cliente_id')
            if not cliente_id:
                raise PermissionDenied('Como admin, debes indicar cliente_id en el body.')
            serializer.save(cliente_id=cliente_id)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Reservación modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Reservación modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reservación eliminada correctamente'}, status=status.HTTP_200_OK)


class ReservacionServicioViewSet(viewsets.ModelViewSet):
    """Mismo criterio de ownership que ReservacionViewSet, via la reservacion padre."""
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
        serializer.save()

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio de reservación eliminado correctamente'}, status=status.HTTP_200_OK)