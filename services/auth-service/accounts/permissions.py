from rest_framework.permissions import BasePermission


class EsClienteOAdmin(BasePermission):
    """
    Acceso solo a usuarios autenticados con rol 'cliente' o 'admin'.
    Por ahora ambos roles tienen los mismos permisos (sin distincion fina todavia).
    """
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )