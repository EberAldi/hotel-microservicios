from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Pago
from .serializers import PagoSerializer
from common.permissions import EsDuenoPagoOAdmin


class PagoViewSet(viewsets.ModelViewSet):
    """
    Requiere JWT con rol 'cliente' o 'admin'.
    - cliente: solo ve/gestiona SUS PROPIOS pagos.
    - admin: ve y gestiona todos.

    Filtros opcionales (solo con efecto real para admin):
      /api/pagos/pagos/?reservacion_id=<uuid>
      /api/pagos/pagos/?estado=pendiente
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
        estado = self.request.query_params.get('estado')
        if reservacion_id:
            queryset = queryset.filter(reservacion_id=reservacion_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.rol == 'cliente':
            serializer.save(cliente_id=usuario.cliente_id)
        else:
            cliente_id = self.request.data.get('cliente_id')
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