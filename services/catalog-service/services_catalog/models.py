import uuid
from django.db import models


class Servicio(models.Model):
    CATEGORIA_CHOICES = [
        ('desayuno', 'Desayuno'),
        ('spa', 'Spa'),
        ('transporte', 'Transporte'),
        ('excursion', 'Excursion'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'servicios'

    def __str__(self):
        return self.nombre