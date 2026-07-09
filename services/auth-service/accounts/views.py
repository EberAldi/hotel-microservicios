from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Usuario, Cliente
from .serializers import UsuarioSerializer, ClienteSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    GET    /api/auth/usuarios/       -> lista
    POST   /api/auth/usuarios/       -> crea
    GET    /api/auth/usuarios/{id}/  -> detalle
    PUT    /api/auth/usuarios/{id}/  -> reemplaza (responde con mensaje simple)
    PATCH  /api/auth/usuarios/{id}/  -> actualiza parcial (responde con mensaje simple)
    DELETE /api/auth/usuarios/{id}/  -> elimina (responde con mensaje simple)

    Sin JWT/roles por ahora (AllowAny) -- se agrega mas adelante.
    """
    queryset = Usuario.objects.all().order_by('-creado_en')
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

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
    Mismo patron CRUD que UsuarioViewSet, para el perfil de negocio del cliente.
    GET/POST en /api/auth/clientes/, GET/PUT/PATCH/DELETE en /api/auth/clientes/{id}/
    """
    queryset = Cliente.objects.select_related('usuario').all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente modificado correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Cliente eliminado correctamente'}, status=status.HTTP_200_OK)