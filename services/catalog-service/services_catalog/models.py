import uuid
from django.db import models


class CategoriaServicio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = 'categorias_servicio'

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.PROTECT, related_name='servicios')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'servicios'

    def __str__(self):
        return self.nombre


def ruta_imagen_servicio(instance, filename):
    return f'servicios/{instance.servicio_id}/{filename}'


class ImagenServicio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=ruta_imagen_servicio)
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'imagenes_servicio'
        ordering = ['orden']

    def __str__(self):
        return f"Imagen {self.orden} de {self.servicio.nombre}"