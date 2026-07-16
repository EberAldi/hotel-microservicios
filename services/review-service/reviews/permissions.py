from rest_framework.permissions import BasePermission


class EsClienteOAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )


class EsDuenoResenaOAdmin(BasePermission):
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
        return str(obj.cliente_id) == str(usuario.cliente_id)


class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) == 'admin'
        )


class EsDuenoRespuestaOAdmin(BasePermission):
    """El autor de la respuesta (admin o cliente) o cualquier admin."""
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
        return obj.autor_tipo == 'cliente' and str(obj.autor_id) == str(usuario.cliente_id)