from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Resena
from .serializers import ResenaSerializer
from .permissions import EsClienteOAdmin


class ResenaViewSet(viewsets.ModelViewSet):
    """
    GET (lista/detalle/filtros)  -> publico, incluso invitado sin token
    POST/PUT/PATCH/DELETE        -> requiere JWT con rol 'cliente' o 'admin'
    """
    serializer_class = ResenaSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        return [EsClienteOAdmin()]

    def get_queryset(self):
        queryset = Resena.objects.all().order_by('-id')
        tipo_objetivo = self.request.query_params.get('tipo_objetivo')
        objetivo_id = self.request.query_params.get('objetivo_id')
        cliente_id = self.request.query_params.get('cliente_id')
        if tipo_objetivo:
            queryset = queryset.filter(tipo_objetivo=tipo_objetivo)
        if objetivo_id:
            queryset = queryset.filter(objetivo_id=objetivo_id)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña eliminada correctamente'}, status=status.HTTP_200_OK)