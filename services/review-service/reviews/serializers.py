from rest_framework import serializers

from .models import Resena


class ResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resena
        fields = ['id', 'cliente_id', 'tipo_objetivo', 'objetivo_id', 'calificacion', 'comentario']
        read_only_fields = ['id', 'cliente_id']