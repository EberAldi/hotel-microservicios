import uuid
from django.db import models


class Room(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('MAINTENANCE', 'Maintenance'),
        ('OUT_OF_SERVICE', 'Out of service'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number      = models.CharField(max_length=10, unique=True)
    type        = models.CharField(max_length=60)
    base_price  = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    class Meta:
        db_table = 'rooms'
