from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response

from .models import TipoHabitacion, Habitacion, ImagenHabitacion, DisponibilidadHabitacion
from .serializers import (
    TipoHabitacionSerializer, HabitacionSerializer,
    ImagenHabitacionSerializer, DisponibilidadHabitacionSerializer,
)
from common.permissions import EsAdmin
from django.db.models import ProtectedError

class TipoHabitacionViewSet(viewsets.ModelViewSet):
    """GET publico. POST/PUT/PATCH/DELETE solo admin."""
    queryset = TipoHabitacion.objects.all().order_by('nombre')
    serializer_class = TipoHabitacionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Tipo de habitación modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Tipo de habitación modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'No se puede eliminar: hay habitaciones que usan este tipo. Reasígnalas o elimínalas primero.'},
                status=status.HTTP_409_CONFLICT
            )
        return Response({'mensaje': 'Tipo de habitación eliminado correctamente'}, status=status.HTTP_200_OK)


class HabitacionViewSet(viewsets.ModelViewSet):
    """
    GET publico. POST/PUT/PATCH/DELETE solo admin.
    Filtros opcionales: ?estado=disponible&tipo=<uuid>
    """
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def get_queryset(self):
        queryset = Habitacion.objects.select_related('tipo').all().order_by('numero')
        estado = self.request.query_params.get('estado')
        tipo = self.request.query_params.get('tipo')
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo:
            queryset = queryset.filter(tipo_id=tipo)
        return queryset

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Habitación eliminada correctamente'}, status=status.HTTP_200_OK)


class ImagenHabitacionViewSet(viewsets.ModelViewSet):
    """GET publico. POST/PUT/PATCH/DELETE solo admin. Filtro: ?habitacion_id=<uuid>"""
    serializer_class = ImagenHabitacionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def get_queryset(self):
        queryset = ImagenHabitacion.objects.select_related('habitacion').all()
        habitacion_id = self.request.query_params.get('habitacion_id')
        if habitacion_id:
            queryset = queryset.filter(habitacion_id=habitacion_id)
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


class DisponibilidadHabitacionViewSet(viewsets.ModelViewSet):
    """
    GET publico. POST/PUT/PATCH/DELETE solo admin.
    Filtros opcionales: ?habitacion_id=<uuid>&fecha=2026-08-01&estado=disponible
    """
    serializer_class = DisponibilidadHabitacionSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [EsAdmin()]

    def get_queryset(self):
        queryset = DisponibilidadHabitacion.objects.select_related('habitacion').all()
        habitacion_id = self.request.query_params.get('habitacion_id')
        fecha = self.request.query_params.get('fecha')
        estado = self.request.query_params.get('estado')
        if habitacion_id:
            queryset = queryset.filter(habitacion_id=habitacion_id)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Disponibilidad modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Disponibilidad modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Disponibilidad eliminada correctamente'}, status=status.HTTP_200_OK)