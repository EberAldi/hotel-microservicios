import uuid
from django.db import models


class Reservacion(models.Model):
    ESTADO_CHOICES = [
        ('draft', 'Draft'),
        ('pendiente_pago', 'Pendiente de pago'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.UUIDField()      # ref. logica -> auth_db.clientes.id
    habitacion_id = models.UUIDField()   # ref. logica -> catalog_db.habitaciones.id
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='draft')
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'reservaciones'

    def __str__(self):
        return f"Reservacion {self.id} ({self.estado})"


class ReservacionServicio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='servicios')
    servicio_id = models.UUIDField()  # ref. logica -> catalog_db.servicios.id
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'reservacion_servicios'

    def __str__(self):
        return f"{self.reservacion_id} - servicio {self.servicio_id} x{self.cantidad}"