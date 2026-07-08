import uuid
from django.db import models


class Payment(models.Model):
    METHOD_CHOICES = [('CARD', 'Card'), ('PAYPAL', 'PayPal'), ('CASH', 'Cash')]
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('REFUNDED', 'Refunded')]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation_id  = models.UUIDField()  # ref. logica -> reservation_svc.reservations.id
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    method          = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id  = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'payments'
