from rest_framework import serializers
from .models import Pago, Factura, Reembolso


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'reservacion_id', 'carrito_id', 'cliente_id', 'monto', 'metodo', 'estado', 'id_transaccion']
        read_only_fields = ['id', 'cliente_id', 'estado']

    def validate(self, data):
        if self.instance is not None and 'reservacion_id' not in data and 'carrito_id' not in data:
            return data

        reservacion_id = data.get('reservacion_id', getattr(self.instance, 'reservacion_id', None))
        carrito_id = data.get('carrito_id', getattr(self.instance, 'carrito_id', None))
        if bool(reservacion_id) == bool(carrito_id):
            raise serializers.ValidationError(
                'Debes indicar exactamente uno: reservacion_id o carrito_id (no ambos, no ninguno).'
            )
        return data


class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ['id', 'pago', 'numero_factura', 'fecha_emision', 'url_pdf']
        read_only_fields = fields


class ReembolsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reembolso
        fields = ['id', 'pago', 'monto', 'motivo', 'estado', 'creado_en']
        read_only_fields = ['id', 'estado', 'creado_en']