import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class UsuarioToken:
    is_authenticated = True

    def __init__(self, id, correo, rol, cliente_id=None):
        self.id = id
        self.correo = correo
        self.rol = rol
        self.cliente_id = cliente_id

    def __str__(self):
        return self.correo


class JWTRolAuthentication(BaseAuthentication):
    """Decodifica el access token emitido por auth-service (PyJWT, firmado
    con JWT_SECRET_KEY/JWT_ALGORITHM, claims usuario_id/correo/rol/type)."""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[len('Bearer '):].strip()
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token invalido.')

        if payload.get('type') != 'access':
            raise AuthenticationFailed('Token invalido: no es un access token.')

        user_id = payload.get('usuario_id')
        rol = payload.get('rol')
        if user_id is None or rol is None:
            raise AuthenticationFailed('Token invalido: faltan claims requeridos.')

        usuario = UsuarioToken(
            id=user_id, correo=payload.get('correo'), rol=rol,
            cliente_id=payload.get('cliente_id'),
        )
        return (usuario, token)
