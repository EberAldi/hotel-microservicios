from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/auth/users/  -> lista usuarios (sin password_hash)
    POST /api/auth/users/  -> crea usuario (hashea password con bcrypt)

    Sin JWT por ahora (AllowAny), a proposito: esto es solo para validar
    que el guardado en la base de datos funciona de punta a punta.
    """
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [AllowAny]