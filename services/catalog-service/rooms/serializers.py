from rest_framework import serializers
from .models import Habitacion


class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ['id', 'numero', 'tipo', 'precio_base', 'estado']
        read_only_fields = ['id']