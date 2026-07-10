import uuid
from django.db import models


class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'Mantenimiento'),
        ('deshabilitada', 'Deshabilitada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=50)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    class Meta:
        db_table = 'habitaciones'

    def __str__(self):
        return f"{self.numero} ({self.tipo})"