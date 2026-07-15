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
        

class Direccion(models.Model):
    """Direcciones de un cliente (envio/facturacion). Un cliente puede tener varias."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones')
    calle = models.CharField(max_length=200)
    numero_exterior = models.CharField(max_length=20, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100)
    estado_provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=100, default='Mexico')
    es_principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'direcciones'

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"


class AuditoriaAcceso(models.Model):
    """
    Bitacora de intentos de login (exitosos y fallidos). Se llena
    automaticamente desde LoginView, no se crea manualmente via API.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='accesos', null=True, blank=True)
    correo_intentado = models.EmailField()  # se guarda aunque el usuario no exista, para detectar ataques
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    exitoso = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_accesos'

    def __str__(self):
        return f"{self.correo_intentado} - {'OK' if self.exitoso else 'FALLO'} - {self.creado_en}"