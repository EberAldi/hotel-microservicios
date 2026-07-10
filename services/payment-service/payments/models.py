import uuid
from django.db import models


class Pago(models.Model):
    METODO_CHOICES = [
        ('tarjeta', 'Tarjeta'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Efectivo'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservacion_id = models.UUIDField()  # ref. logica -> reservation_db.reservaciones.id
    cliente_id = models.UUIDField()      # ref. logica -> auth_db.clientes.id (denormalizado para ownership)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    id_transaccion = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'pagos'

    def __str__(self):
        return f"Pago {self.id} - {self.estado}"