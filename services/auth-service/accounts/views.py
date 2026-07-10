import bcrypt
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Usuario, Cliente, TokenRefresco
from .serializers import UsuarioSerializer, ClienteSerializer
from .permissions import EsAdmin, EsPropioUsuarioOAdmin, EsPropioClienteOAdmin
from .utils import hash_token


def _claims_para(usuario):
    """Arma los claims comunes (correo, rol, cliente_id) para access y refresh."""
    cliente = Cliente.objects.filter(usuario=usuario).first()
    return {
        'correo': usuario.correo,
        'rol': usuario.rol,
        'cliente_id': str(cliente.id) if cliente else None,
    }


class LoginView(APIView):
    """POST /api/auth/login/  body: {"correo": "...", "contrasena": "..."}"""
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo')
        contrasena = request.data.get('contrasena')
        if not correo or not contrasena:
            return Response({'detail': 'correo y contrasena son requeridos.'}, status=400)

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response({'detail': 'Credenciales invalidas.'}, status=401)

        if not bcrypt.checkpw(contrasena.encode('utf-8'), usuario.contrasena_hash.encode('utf-8')):
            return Response({'detail': 'Credenciales invalidas.'}, status=401)

        if usuario.estado_cuenta != 'activo':
            return Response({'detail': 'Cuenta inactiva o suspendida.'}, status=403)

        claims = _claims_para(usuario)

        refresh = SimpleJWTRefreshToken.for_user(usuario)
        for k, v in claims.items():
            refresh[k] = v
        access = refresh.access_token
        for k, v in claims.items():
            access[k] = v

        TokenRefresco.objects.create(
            usuario=usuario,
            token_hash=hash_token(str(refresh)),
            expira_en=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            revocado=False,
        )

        return Response({'access': str(access), 'refresh': str(refresh), 'rol': usuario.rol})


class RefreshView(APIView):
    """
    POST /api/auth/login/refresh/  body: {"refresh": "..."}
    Reemplaza el TokenRefreshView por defecto de SimpleJWT porque necesitamos
    checar la tabla refresh_tokens (revocado/expirado a la fuerza), no solo
    la firma/expiracion criptografica del token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('refresh')
        if not token_str:
            return Response({'detail': 'refresh es requerido.'}, status=400)

        try:
            token = SimpleJWTRefreshToken(token_str)
        except TokenError:
            return Response({'detail': 'Refresh token invalido o expirado.'}, status=401)

        try:
            registro = TokenRefresco.objects.get(token_hash=hash_token(token_str))
        except TokenRefresco.DoesNotExist:
            return Response({'detail': 'Refresh token no reconocido.'}, status=401)

        if registro.revocado:
            return Response({'detail': 'Refresh token revocado.'}, status=401)
        if registro.expira_en < timezone.now():
            return Response({'detail': 'Refresh token expirado.'}, status=401)

        claims = _claims_para(registro.usuario)
        access = token.access_token
        for k, v in claims.items():
            access[k] = v

        return Response({'access': str(access)})


class LogoutView(APIView):
    """POST /api/auth/logout/  body: {"refresh": "..."} -> revoca ese refresh token."""
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get('refresh')
        if not token_str:
            return Response({'detail': 'refresh es requerido.'}, status=400)

        actualizados = TokenRefresco.objects.filter(token_hash=hash_token(token_str)).update(revocado=True)
        if not actualizados:
            return Response({'detail': 'Refresh token no reconocido.'}, status=404)
        return Response({'mensaje': 'Sesion cerrada correctamente.'})


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    POST (registro)         -> publico
    GET lista                -> solo admin
    GET/PUT/PATCH detalle    -> el propio usuario o admin
    DELETE                   -> solo admin
    """
    queryset = Usuario.objects.all().order_by('-creado_en')
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('list', 'destroy'):
            return [EsAdmin()]
        return [EsPropioUsuarioOAdmin()]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario eliminado correctamente'}, status=status.HTTP_200_OK)
    def perform_create(self, serializer):
        # El registro publico SIEMPRE crea 'cliente', sin importar que el
        # body mande otro rol -- evita que cualquiera se auto-declare admin.
        serializer.save(rol='cliente')


class ClienteViewSet(viewsets.ModelViewSet):
    """
    POST                      -> cliente crea SU PROPIO perfil (o admin, cualquiera)
    GET lista                 -> solo admin
    GET/PUT/PATCH/DELETE      -> el propio dueño o admin
    """
    queryset = Cliente.objects.select_related('usuario').all()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [EsAdmin()]
        return [EsPropioClienteOAdmin()]

    def perform_create(self, serializer):
        usuario_token = self.request.user
        if usuario_token.rol == 'cliente':
            # un cliente solo puede crear SU PROPIO perfil, sin importar que mande en el body
            serializer.save(usuario_id=usuario_token.id)
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente eliminado correctamente'}, status=status.HTTP_200_OK)