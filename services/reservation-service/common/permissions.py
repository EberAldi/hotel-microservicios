from rest_framework.permissions import BasePermission


class EsDuenoReservacionOAdmin(BasePermission):
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


class EsDuenoReservacionServicioOAdmin(BasePermission):
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
        return str(obj.reservacion.cliente_id) == str(usuario.cliente_id)