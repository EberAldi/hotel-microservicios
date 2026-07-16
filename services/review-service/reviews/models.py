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
    ESTADO_CHOICES = [
        ('aprobada', 'Aprobada'),
        ('oculta', 'Oculta'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.UUIDField()
    tipo_objetivo = models.CharField(max_length=20, choices=TIPO_OBJETIVO_CHOICES)
    objetivo_id = models.UUIDField()
    calificacion = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='aprobada')

    class Meta:
        db_table = 'resenas'
        indexes = [models.Index(fields=['tipo_objetivo', 'objetivo_id'])]

    def __str__(self):
        return f"{self.tipo_objetivo} {self.objetivo_id} - {self.calificacion}"


class RespuestaResena(models.Model):
    """
    Respuesta a una resena. Puede responder el hotel (admin) o cualquier
    otro cliente (hilo de comentarios abierto). autor_id es referencia
    logica: usuario_id si autor_tipo='admin', cliente_id si autor_tipo='cliente'.
    """
    AUTOR_TIPO_CHOICES = [
        ('admin', 'Admin'),
        ('cliente', 'Cliente'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resena = models.ForeignKey(Resena, on_delete=models.CASCADE, related_name='respuestas')
    autor_tipo = models.CharField(max_length=20, choices=AUTOR_TIPO_CHOICES)
    autor_id = models.UUIDField()
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'respuestas_resena'
        ordering = ['creado_en']

    def __str__(self):
        return f"Respuesta de {self.autor_tipo} a {self.resena_id}"