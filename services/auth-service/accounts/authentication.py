from rest_framework import permissions


class EsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == "admin")


class EsPropioUsuarioOAdmin(permissions.BasePermission):
    """Para el recurso Usuario: el propio usuario o un admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.rol == "admin":
            return True
        return obj.id == request.user.id


class EsPropioClienteOAdmin(permissions.BasePermission):
    """Para Cliente y Direccion: el dueño del perfil o un admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.rol == "admin":
            return True
        cliente = getattr(request.user, "cliente", None)
        if cliente is None:
            return False
        if hasattr(obj, "usuario_id"):  # es un Cliente
            return obj.id == cliente.id
        return obj.cliente_id == cliente.id  # es una Direccion
