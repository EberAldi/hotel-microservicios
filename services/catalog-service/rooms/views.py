from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response

from .models import Habitacion
from .serializers import HabitacionSerializer
from common.permissions import EsAdmin


class HabitacionViewSet(viewsets.ModelViewSet):
    """
    GET (lista/detalle)          -> publico, incluso invitado sin token
    POST/PUT/PATCH/DELETE        -> requiere JWT con rol 'admin'
    """
    queryset = Habitacion.objects.all().order_by('numero')
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación eliminada correctamente'}, status=status.HTTP_200_OK)