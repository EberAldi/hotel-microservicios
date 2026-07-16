from rest_framework import serializers

from .models import Resena, RespuestaResena


class ResenaSerializer(serializers.ModelSerializer):
    """
    'cliente_id' y 'estado' son read-only: cliente_id se asigna desde el
    token, estado solo se cambia via el endpoint /moderar/ (solo admin).
    """
    class Meta:
        model = Resena
        fields = ['id', 'cliente_id', 'tipo_objetivo', 'objetivo_id', 'calificacion', 'comentario', 'estado']
        read_only_fields = ['id', 'cliente_id', 'estado']


class RespuestaResenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaResena
        fields = ['id', 'resena', 'autor_tipo', 'autor_id', 'contenido', 'creado_en']
        read_only_fields = ['id', 'autor_tipo', 'autor_id', 'creado_en']