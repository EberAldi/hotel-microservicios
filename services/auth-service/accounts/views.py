import hashlib

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditoriaAcceso, Cliente, Direccion, RefreshToken as RefreshTokenModel, Usuario
from .permissions import EsAdmin, EsPropioClienteOAdmin, EsPropioUsuarioOAdmin
from .serializers import (
    AuditoriaAccesoSerializer, ClienteCrearSerializer, ClienteSerializer,
    DireccionCrearSerializer, DireccionSerializer, LoginSerializer,
    LogoutSerializer, RefreshSerializer, UsuarioActualizarSerializer,
    UsuarioCrearSerializer, UsuarioSerializer,
)
from .utils import generar_access_token, generar_refresh_token


def _hash_token(token_plano: str) -> str:
    return hashlib.sha256(token_plano.encode()).hexdigest()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correo = serializer.validated_data["correo"]
        contrasena = serializer.validated_data["contrasena"]

        usuario = Usuario.objects.filter(correo__iexact=correo).first()
        exitoso = bool(usuario and usuario.check_password(contrasena))

        # el intento se guarda SIEMPRE, exista o no el usuario
        AuditoriaAcceso.objects.create(
            usuario=usuario,
            correo_intentado=correo,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            exitoso=exitoso,
        )

        if not exitoso:
            return Response({"detail": "Credenciales invalidas"}, status=status.HTTP_401_UNAUTHORIZED)
        if usuario.estado_cuenta != "activo":
            return Response({"detail": "Cuenta inactiva o suspendida"}, status=status.HTTP_403_FORBIDDEN)

        access = generar_access_token(usuario)
        refresh_plano, expira_en = generar_refresh_token()
        RefreshTokenModel.objects.create(
            usuario=usuario, token_hash=_hash_token(refresh_plano), expira_en=expira_en,
        )
        return Response({"access": access, "refresh": refresh_plano, "rol": usuario.rol})


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_plano = serializer.validated_data["refresh"]

        registro = (
            RefreshTokenModel.objects.filter(token_hash=_hash_token(refresh_plano), revocado=False)
            .select_related("usuario").first()
        )
        if not registro or registro.expira_en < timezone.now():
            return Response({"detail": "Refresh token invalido, expirado o revocado"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"access": generar_access_token(registro.usuario)})


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_plano = serializer.validated_data["refresh"]

        registro = RefreshTokenModel.objects.filter(token_hash=_hash_token(refresh_plano)).first()
        if not registro:
            return Response({"detail": "Refresh token no reconocido"}, status=status.HTTP_404_NOT_FOUND)

        registro.revocado = True
        registro.save(update_fields=["revocado"])
        return Response({"mensaje": "Sesion cerrada correctamente"})


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ("list", "destroy"):
            return [EsAdmin()]
        return [permissions.IsAuthenticated(), EsPropioUsuarioOAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCrearSerializer
        if self.action in ("update", "partial_update"):
            return UsuarioActualizarSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        serializer.save(rol="cliente")  # el rol se fuerza en el servidor

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.pop("password", None)
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return Response({"mensaje": "Usuario modificado correctamente"})

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"mensaje": "Usuario eliminado correctamente"})


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()

    def get_permissions(self):
        if self.action == "list":
            return [EsAdmin()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), EsPropioClienteOAdmin()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ClienteCrearSerializer
        return ClienteSerializer

    def perform_create(self, serializer):
        if Cliente.objects.filter(usuario=self.request.user).exists():
            raise ValidationError("Este usuario ya tiene un perfil de cliente")
        serializer.save(usuario=self.request.user)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"mensaje": "Cliente modificado correctamente"})

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"mensaje": "Cliente eliminado correctamente"})


class DireccionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.request.user.rol == "admin":
            return Direccion.objects.all()
        cliente = getattr(self.request.user, "cliente", None)
        return Direccion.objects.filter(cliente=cliente) if cliente else Direccion.objects.none()

    def get_permissions(self):
        return [permissions.IsAuthenticated(), EsPropioClienteOAdmin()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DireccionCrearSerializer
        return DireccionSerializer

    def perform_create(self, serializer):
        if self.request.user.rol == "admin":
            serializer.save()  # espera 'cliente' en el body
        else:
            cliente = getattr(self.request.user, "cliente", None)
            serializer.save(cliente=cliente)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"mensaje": "Direccion modificada correctamente"})

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"mensaje": "Direccion eliminada correctamente"})


class AuditoriaAccesoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditoriaAcceso.objects.all().order_by("-creado_en")
    serializer_class = AuditoriaAccesoSerializer
    permission_classes = [EsAdmin]
