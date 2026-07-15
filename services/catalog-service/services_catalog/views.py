from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response

from .models import CategoriaServicio, Servicio, ImagenServicio
from .serializers import CategoriaServicioSerializer, ServicioSerializer, ImagenServicioSerializer
from common.permissions import EsAdmin
from django.db.models import ProtectedError

class CategoriaServicioViewSet(viewsets.ModelViewSet):
    """GET publico. POST/PUT/PATCH/DELETE solo admin."""
    queryset = CategoriaServicio.objects.all().order_by('nombre')
    serializer_class = CategoriaServicioSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Categoría modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Categoría modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Categoría eliminada correctamente'}, status=status.HTTP_200_OK)


class ServicioViewSet(viewsets.ModelViewSet):
    """GET publico. POST/PUT/PATCH/DELETE solo admin. Filtro: ?categoria=<uuid>"""
    serializer_class = ServicioSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def get_queryset(self):
        queryset = Servicio.objects.select_related('categoria').all().order_by('nombre')
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Servicio eliminado correctamente'}, status=status.HTTP_200_OK)


class ImagenServicioViewSet(viewsets.ModelViewSet):
    """GET publico. POST/PUT/PATCH/DELETE solo admin. Filtro: ?servicio_id=<uuid>"""
    serializer_class = ImagenServicioSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def get_queryset(self):
        queryset = ImagenServicio.objects.select_related('servicio').all()
        servicio_id = self.request.query_params.get('servicio_id')
        if servicio_id:
            queryset = queryset.filter(servicio_id=servicio_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Imagen modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Imagen modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Imagen eliminada correctamente'}, status=status.HTTP_200_OK)