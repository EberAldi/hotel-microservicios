import uuid
from django.db import models


class Reservation(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled')]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id   = models.UUIDField()   # ref. logica -> auth_svc.customers.id
    room_id       = models.UUIDField()   # ref. logica -> catalog_svc.rooms.id
    check_in      = models.DateField()
    check_out     = models.DateField()
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price   = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'reservations'


class ReservationService(models.Model):
    """Tabla puente 'incluye' / 'es_incluido' entre reservations y catalog_svc.services."""
    reservation = models.ForeignKey(Reservation, related_name='reservation_services', on_delete=models.CASCADE)
    service_id  = models.UUIDField()  # ref. logica -> catalog_svc.services.id
    quantity    = models.IntegerField(default=1)

    class Meta:
        db_table = 'reservation_services'
        unique_together = ('reservation', 'service_id')
