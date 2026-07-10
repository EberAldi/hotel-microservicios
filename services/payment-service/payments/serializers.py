from rest_framework import serializers
from .models import Pago


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'reservacion_id', 'cliente_id', 'monto', 'metodo', 'estado', 'id_transaccion']
        read_only_fields = ['id', 'cliente_id']