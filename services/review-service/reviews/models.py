import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Resena polimorfica: target_type indica si target_id es un ROOM, RESERVATION o SERVICE."""
    TARGET_CHOICES = [('ROOM', 'Room'), ('RESERVATION', 'Reservation'), ('SERVICE', 'Service')]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id   = models.UUIDField()  # ref. logica -> auth_svc.customers.id
    target_type   = models.CharField(max_length=20, choices=TARGET_CHOICES)
    target_id     = models.UUIDField()  # ref. logica, segun target_type
    rating        = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment       = models.TextField(blank=True)

    class Meta:
        db_table = 'reviews'
        indexes = [models.Index(fields=['target_type', 'target_id'])]
