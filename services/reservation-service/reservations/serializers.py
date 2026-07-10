from rest_framework import serializers
from .models import Reservacion, ReservacionServicio


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = ['id', 'cliente_id', 'habitacion_id', 'fecha_entrada', 'fecha_salida', 'estado', 'precio_total']
        read_only_fields = ['id', 'cliente_id']


class ReservacionServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservacionServicio
        fields = ['id', 'reservacion', 'servicio_id', 'cantidad']
        read_only_fields = ['id']