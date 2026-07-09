from rest_framework import serializers

from .models import Resena


class ResenaSerializer(serializers.ModelSerializer):
    """
    Resena polimorfica: tipo_objetivo indica si objetivo_id es HABITACION,
    RESERVACION o SERVICIO. Sin JWT/roles por ahora: 'cliente_id' se manda
    explicitamente en el body (mas adelante, con JWT, se tomara del token).
    """
    class Meta:
        model = Resena
        fields = ['id', 'cliente_id', 'tipo_objetivo', 'objetivo_id', 'calificacion', 'comentario']
        read_only_fields = ['id']