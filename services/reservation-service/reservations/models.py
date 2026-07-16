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
    cliente_id = models.UUIDField()
    habitacion_id = models.UUIDField()
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
    servicio_id = models.UUIDField()
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'reservacion_servicios'

    def __str__(self):
        return f"{self.reservacion_id} - servicio {self.servicio_id} x{self.cantidad}"


class HistorialEstadoReservacion(models.Model):
    """
    Bitacora de cambios de estado. Se llena automaticamente desde
    ReservacionViewSet cuando 'estado' cambia -- solo lectura via API.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20)
    motivo = models.CharField(max_length=255, blank=True)
    cambiado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_estados_reservacion'
        ordering = ['-cambiado_en']

    def __str__(self):
        return f"{self.reservacion_id}: {self.estado_anterior} -> {self.estado_nuevo}"


class Carrito(models.Model):
    """
    Carrito de servicios sueltos (spa, transporte, excursion...) SIN
    necesidad de reservacion. Solo contiene SERVICIOs, nunca habitaciones
    (esas siempre van por Reservacion directa).
    """
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('pendiente_pago', 'Pendiente de pago'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('expirado', 'Expirado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente_id = models.UUIDField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'carritos'

    def __str__(self):
        return f"Carrito {self.id} ({self.estado})"


class CarritoItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    servicio_id = models.UUIDField()
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_uso = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'carrito_items'

    def __str__(self):
        return f"{self.carrito_id} - servicio {self.servicio_id} x{self.cantidad}"