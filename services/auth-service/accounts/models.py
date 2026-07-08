import uuid
from django.db import models


class User(models.Model):
    ROLE_CHOICES = [('CUSTOMER', 'Customer'), ('ADMIN', 'Admin'), ('STAFF', 'Staff')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('SUSPENDED', 'Suspended'), ('DELETED', 'Deleted')]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email           = models.EmailField(unique=True)
    password_hash   = models.CharField(max_length=255)
    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    account_status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'


class Customer(models.Model):
    """Relacion 'es': 1 user <-> 1 perfil de customer (opcional, staff no tiene fila aqui)."""
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user                = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    full_name           = models.CharField(max_length=150)
    phone               = models.CharField(max_length=20, blank=True)
    preferred_language  = models.CharField(max_length=10, blank=True)
    loyalty_points      = models.IntegerField(default=0)

    class Meta:
        db_table = 'customers'
