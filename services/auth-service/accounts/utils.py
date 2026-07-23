import datetime
import secrets
import jwt
from django.conf import settings

from .models import Cliente


def generar_access_token(usuario):
    cliente = Cliente.objects.filter(usuario_id=usuario.id).first()
    payload = {
        "usuario_id": str(usuario.id),
        "correo": usuario.correo,
        "rol": usuario.rol,
        "cliente_id": str(cliente.id) if cliente else None,
        "exp": datetime.datetime.utcnow() + settings.JWT_ACCESS_TOKEN_LIFETIME,
        "iat": datetime.datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def generar_refresh_token():
    token_plano = secrets.token_urlsafe(48)
    expira_en = datetime.datetime.utcnow() + settings.JWT_REFRESH_TOKEN_LIFETIME
    return token_plano, expira_en