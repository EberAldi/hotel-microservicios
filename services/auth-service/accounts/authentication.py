from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class UsuarioToken:
    """
    Representa al usuario autenticado, reconstruido SOLO a partir de los
    claims del JWT (sin consultar la base de datos en cada request).
    """
    is_authenticated = True

    def __init__(self, id, correo, rol):
        self.id = id
        self.correo = correo
        self.rol = rol

    def __str__(self):
        return self.correo


class JWTRolAuthentication(JWTAuthentication):
    """
    Valida firma y expiracion del JWT igual que JWTAuthentication normal,
    pero arma el usuario autenticado directo desde los claims del token
    (id, correo, rol) en vez de buscarlo en una tabla.
    """
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        correo = validated_token.get('correo')
        rol = validated_token.get('rol')
        if user_id is None or rol is None:
            raise AuthenticationFailed('Token invalido: faltan claims requeridos.')
        return UsuarioToken(id=user_id, correo=correo, rol=rol)