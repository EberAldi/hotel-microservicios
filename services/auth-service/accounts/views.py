import bcrypt
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario, Cliente
from .serializers import UsuarioSerializer, ClienteSerializer
from .permissions import EsClienteOAdmin


class LoginView(APIView):
    """
    POST /api/auth/login/
    Body: {"correo": "...", "contrasena": "..."}
    Devuelve access + refresh token, con claims custom (user_id, correo, rol).
    Sin sesion en el servidor: el token lleva todo lo necesario.
    """
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

        refresh = RefreshToken.for_user(usuario)
        refresh['correo'] = usuario.correo
        refresh['rol'] = usuario.rol

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'rol': usuario.rol,
        })


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Requiere JWT valido con rol 'cliente' o 'admin' para TODO (incluido GET).
    El invitado (sin token) no tiene acceso a nada de este recurso.
    """
    queryset = Usuario.objects.all().order_by('-creado_en')
    serializer_class = UsuarioSerializer
    permission_classes = [EsClienteOAdmin]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Usuario eliminado correctamente'}, status=status.HTTP_200_OK)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    Mismo criterio de acceso que UsuarioViewSet.
    """
    queryset = Cliente.objects.select_related('usuario').all()
    serializer_class = ClienteSerializer
    permission_classes = [EsClienteOAdmin]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente eliminado correctamente'}, status=status.HTTP_200_OK)