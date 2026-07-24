from rest_framework import permissions


class EsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == "admin")


class EsPropioUsuarioOAdmin(permissions.BasePermission):
    """Para el recurso Usuario: el propio usuario o un admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.rol == "admin":
            return True
        # obj.id es un UUID real; request.user.id viene del JWT como string
        # -- hay que comparar como texto en ambos lados, si no NUNCA coinciden.
        return str(obj.id) == str(request.user.id)


class EsPropioClienteOAdmin(permissions.BasePermission):
    """Para Cliente y Direccion: el dueño del perfil o un admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.rol == "admin":
            return True
        # request.user es UsuarioToken (armado del JWT), NO un Usuario real
        # de Django -- no tiene relacion .cliente navegable. cliente_id ya
        # viene directo como claim en el token, se usa asi.
        cliente_id = getattr(request.user, "cliente_id", None)
        if cliente_id is None:
            return False
        if hasattr(obj, "usuario_id"):  # es un Cliente
            return str(obj.id) == str(cliente_id)
        return str(obj.cliente_id) == str(cliente_id)  # es una Direccion