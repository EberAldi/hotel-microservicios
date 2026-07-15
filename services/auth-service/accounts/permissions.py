from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) == 'admin'
        )


class EsClienteOAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )


class EsPropioUsuarioOAdmin(BasePermission):
    """Para el recurso Usuario: solo el propio usuario o un admin."""
    def has_permission(self, request, view):
        usuario = request.user
        return bool(usuario and getattr(usuario, 'is_authenticated', False))

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        if getattr(usuario, 'rol', None) == 'admin':
            return True
        return str(obj.id) == str(usuario.id)


class EsPropioClienteOAdmin(BasePermission):
    """Para el recurso Cliente: solo el dueño del perfil (por su usuario) o un admin."""
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        if getattr(usuario, 'rol', None) == 'admin':
            return True
        return str(obj.usuario_id) == str(usuario.id)
    
class EsDuenoDireccionOAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )

    def has_object_permission(self, request, view, obj):
        usuario = request.user
        if usuario.rol == 'admin':
            return True
        return str(obj.cliente.usuario_id) == str(usuario.id)