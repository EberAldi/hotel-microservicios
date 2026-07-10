from rest_framework import serializers
from .models import Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'categoria', 'precio']
        read_only_fields = ['id']