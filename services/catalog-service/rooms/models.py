import uuid
from django.db import models


class TipoHabitacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    capacidad_maxima = models.PositiveIntegerField()

    class Meta:
        db_table = 'tipos_habitacion'

    def __str__(self):
        return self.nombre


class Habitacion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'Mantenimiento'),
        ('deshabilitada', 'Deshabilitada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=20, unique=True)
    tipo = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name='habitaciones')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    class Meta:
        db_table = 'habitaciones'

    def __str__(self):
        return f"{self.numero} ({self.tipo.nombre})"


def ruta_imagen_habitacion(instance, filename):
    return f'habitaciones/{instance.habitacion_id}/{filename}'


class ImagenHabitacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=ruta_imagen_habitacion)
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'imagenes_habitacion'
        ordering = ['orden']

    def __str__(self):
        return f"Imagen {self.orden} de {self.habitacion.numero}"


class DisponibilidadHabitacion(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('bloqueada', 'Bloqueada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='disponibilidad')
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')

    class Meta:
        db_table = 'disponibilidad_habitacion'
        unique_together = ('habitacion', 'fecha')
        ordering = ['fecha']

    def __str__(self):
        return f"{self.habitacion.numero} - {self.fecha} - {self.estado}"