from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class UsuarioToken:
    is_authenticated = True

    def __init__(self, id, correo, rol):
        self.id = id
        self.correo = correo
        self.rol = rol

    def __str__(self):
        return self.correo


class JWTRolAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        correo = validated_token.get('correo')
        rol = validated_token.get('rol')
        if user_id is None or rol is None:
            raise AuthenticationFailed('Token invalido: faltan claims requeridos.')
        return UsuarioToken(id=user_id, correo=correo, rol=rol)