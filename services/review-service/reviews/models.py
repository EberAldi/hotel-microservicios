import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Resena(models.Model):
    """Resena polimorfica: tipo_objetivo indica si objetivo_id es HABITACION, RESERVACION o SERVICIO."""
    TIPO_OBJETIVO_CHOICES = [
        ('HABITACION', 'Habitacion'),
        ('RESERVACION', 'Reservacion'),
        ('SERVICIO', 'Servicio'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.UUIDField()  # ref. logica -> auth_db.clientes.id
    tipo_objetivo = models.CharField(max_length=20, choices=TIPO_OBJETIVO_CHOICES)
    objetivo_id = models.UUIDField()  # ref. logica, segun tipo_objetivo
    calificacion = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)

    class Meta:
        db_table = 'resenas'
        indexes = [models.Index(fields=['tipo_objetivo', 'objetivo_id'])]

    def __str__(self):
        return f"{self.tipo_objetivo} {self.objetivo_id} - {self.calificacion}"