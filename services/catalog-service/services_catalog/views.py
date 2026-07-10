from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response

from .models import Servicio
from .serializers import ServicioSerializer
from common.permissions import EsAdmin


class ServicioViewSet(viewsets.ModelViewSet):
    """
    GET (lista/detalle)          -> publico, incluso invitado sin token
    POST/PUT/PATCH/DELETE        -> requiere JWT con rol 'admin'
    """
    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio eliminado correctamente'}, status=status.HTTP_200_OK)