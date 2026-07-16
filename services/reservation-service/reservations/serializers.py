from rest_framework import serializers
from .models import Reservacion, ReservacionServicio, HistorialEstadoReservacion, Carrito, CarritoItem


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = ['id', 'cliente_id', 'habitacion_id', 'fecha_entrada', 'fecha_salida', 'estado', 'precio_total']
        read_only_fields = ['id', 'cliente_id']


class ReservacionServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservacionServicio
        fields = ['id', 'reservacion', 'servicio_id', 'cantidad', 'precio_unitario']
        read_only_fields = ['id', 'precio_unitario']


class HistorialEstadoReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstadoReservacion
        fields = ['id', 'reservacion', 'estado_anterior', 'estado_nuevo', 'motivo', 'cambiado_en']
        read_only_fields = fields


class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = ['id', 'cliente_id', 'estado', 'creado_en', 'expira_en']
        read_only_fields = ['id', 'cliente_id', 'estado', 'creado_en']


class CarritoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoItem
        fields = ['id', 'carrito', 'servicio_id', 'cantidad', 'precio_unitario_snapshot', 'fecha_uso']
        read_only_fields = ['id', 'precio_unitario_snapshot']