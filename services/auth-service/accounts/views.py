from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Usuario, Cliente
from .serializers import UsuarioSerializer, ClienteSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    GET    /api/auth/usuarios/       -> lista
    POST   /api/auth/usuarios/       -> crea
    GET    /api/auth/usuarios/{id}/  -> detalle
    PUT    /api/auth/usuarios/{id}/  -> reemplaza
    PATCH  /api/auth/usuarios/{id}/  -> actualiza parcial
    DELETE /api/auth/usuarios/{id}/  -> elimina

    Sin JWT/roles por ahora (AllowAny) -- se agrega mas adelante.
    """
    queryset = Usuario.objects.all().order_by('-creado_en')
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]


class ClienteViewSet(viewsets.ModelViewSet):
    """
    Mismo patron CRUD que UsuarioViewSet, para el perfil de negocio del cliente.
    GET/POST en /api/auth/clientes/, GET/PUT/PATCH/DELETE en /api/auth/clientes/{id}/
    """
    queryset = Cliente.objects.select_related('usuario').all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]