from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Resena
from .serializers import ResenaSerializer
from .permissions import EsClienteOAdmin, EsDuenoResenaOAdmin


class ResenaViewSet(viewsets.ModelViewSet):
    """
    GET (lista/detalle/filtros)  -> publico, incluso invitado sin token
    POST                          -> requiere JWT con rol 'cliente' o 'admin'
    PUT/PATCH/DELETE              -> solo el dueño de la reseña o admin

    Filtros opcionales por query param:
      /api/resenas/resenas/?tipo_objetivo=HABITACION&objetivo_id=<uuid>
      /api/resenas/resenas/?cliente_id=<uuid>
    """
    serializer_class = ResenaSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        if self.action == 'create':
            return [EsClienteOAdmin()]
        return [EsDuenoResenaOAdmin()]

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
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña eliminada correctamente'}, status=status.HTTP_200_OK)