import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError("El usuario debe tener un correo")
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault("rol", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(correo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_CHOICES = [("cliente", "Cliente"), ("admin", "Admin")]
    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("suspendido", "Suspendido"),
        ("inactivo", "Inactivo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correo = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=255, db_column="contrasena_hash")
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="cliente")
    estado_cuenta = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo")
    creado_en = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return self.correo


class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, db_column="usuario_id", related_name="cliente"
    )
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    idioma_preferido = models.CharField(max_length=10, default="es")
    puntos_lealtad = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "clientes"

    def __str__(self):
        return self.nombre_completo


class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column="usuario_id", related_name="refresh_tokens"
    )
    token_hash = models.CharField(max_length=255)
    expira_en = models.DateTimeField()
    revocado = models.BooleanField(default=False)

    class Meta:
        db_table = "refresh_tokens"


class Direccion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, db_column="cliente_id", related_name="direcciones"
    )
    calle = models.CharField(max_length=200)
    numero_exterior = models.CharField(max_length=20, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100)
    estado_provincia = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=100, default="Mexico")
    es_principal = models.BooleanField(default=False)

    class Meta:
        db_table = "direcciones"


class AuditoriaAcceso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="usuario_id",
        related_name="accesos", null=True, blank=True,
    )
    correo_intentado = models.EmailField(max_length=150)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    exitoso = models.BooleanField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auditoria_accesos"
