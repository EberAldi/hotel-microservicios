import uuid
from django.db import models


class Usuario(models.Model):
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Admin'),
    ]
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('inactivo', 'Inactivo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correo = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')
    estado_cuenta = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.correo


class Cliente(models.Model):
    """Relacion 1 a 1 con Usuario (perfil de negocio; admin no tiene fila aqui)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    idioma_preferido = models.CharField(max_length=10, blank=True)
    puntos_lealtad = models.IntegerField(default=0)

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return self.nombre_completo
    
class TokenRefresco(models.Model):
    """
    Registro de refresh tokens emitidos, para poder revocarlos (logout,
    blacklist). No se guarda el token en texto plano, solo su hash.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_hash = models.CharField(max_length=255, unique=True)
    expira_en = models.DateTimeField()
    revocado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'refresh_tokens'