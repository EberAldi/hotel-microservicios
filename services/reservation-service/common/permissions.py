from rest_framework.permissions import BasePermission


class EsClienteOAdmin(BasePermission):
    """Chequeo de rol nada mas (sin ownership por objeto). Para recursos
    de solo lectura donde el queryset ya filtra por dueño."""
    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and getattr(usuario, 'is_authenticated', False)
            and getattr(usuario, 'rol', None) in ('cliente', 'admin')
        )


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


class EsDuenoCarritoOAdmin(BasePermission):
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


class EsDuenoCarritoItemOAdmin(BasePermission):
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
        return str(obj.carrito.cliente_id) == str(usuario.cliente_id)