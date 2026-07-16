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
    reservacion_id = models.UUIDField(null=True, blank=True)
    carrito_id = models.UUIDField(null=True, blank=True)
    cliente_id = models.UUIDField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    id_transaccion = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'pagos'
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(reservacion_id__isnull=False, carrito_id__isnull=True) |
                    models.Q(reservacion_id__isnull=True, carrito_id__isnull=False)
                ),
                name='pago_reservacion_xor_carrito',
            )
        ]

    def __str__(self):
        return f"Pago {self.id} - {self.estado}"


class Factura(models.Model):
    """Se crea automaticamente cuando un Pago pasa a estado='exitoso'."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='factura')
    numero_factura = models.CharField(max_length=30, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    url_pdf = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'facturas'

    def __str__(self):
        return self.numero_factura


class Reembolso(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='reembolsos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reembolsos'

    def __str__(self):
        return f"Reembolso {self.id} ({self.estado})"