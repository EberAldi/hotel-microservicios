from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Resena
from .serializers import ResenaSerializer


class ResenaViewSet(viewsets.ModelViewSet):
    """
    GET    /api/resenas/resenas/       -> lista (soporta filtros por query param)
    POST   /api/resenas/resenas/       -> crea
    GET    /api/resenas/resenas/{id}/  -> detalle
    PUT    /api/resenas/resenas/{id}/  -> reemplaza (responde con mensaje simple)
    PATCH  /api/resenas/resenas/{id}/  -> actualiza parcial (responde con mensaje simple)
    DELETE /api/resenas/resenas/{id}/  -> elimina (responde con mensaje simple)

    Filtros opcionales por query param:
      /api/resenas/resenas/?tipo_objetivo=HABITACION&objetivo_id=<uuid>
      /api/resenas/resenas/?cliente_id=<uuid>
    """
    serializer_class = ResenaSerializer
    permission_classes = [AllowAny]

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