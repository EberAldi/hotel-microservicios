import uuid
from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Admin'),
    ]
    STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('inactivo', 'Inactivo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_column='correo')
    password_hash = models.CharField(max_length=255, db_column='contrasena_hash')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cliente', db_column='rol')
    account_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='activo', db_column='estado_cuenta')
    created_at = models.DateTimeField(auto_now_add=True, db_column='creado_en')

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.email