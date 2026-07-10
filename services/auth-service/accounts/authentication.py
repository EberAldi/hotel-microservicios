from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class UsuarioToken:
    """Usuario autenticado, reconstruido solo desde los claims del JWT."""
    is_authenticated = True

    def __init__(self, id, correo, rol, cliente_id=None):
        self.id = id
        self.correo = correo
        self.rol = rol
        self.cliente_id = cliente_id  # None si el usuario es admin sin perfil de cliente

    def __str__(self):
        return self.correo


class JWTRolAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        correo = validated_token.get('correo')
        rol = validated_token.get('rol')
        cliente_id = validated_token.get('cliente_id')
        if user_id is None or rol is None:
            raise AuthenticationFailed('Token invalido: faltan claims requeridos.')
        return UsuarioToken(id=user_id, correo=correo, rol=rol, cliente_id=cliente_id)