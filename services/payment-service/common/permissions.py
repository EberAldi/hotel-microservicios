from rest_framework.permissions import BasePermission


class EsDuenoPagoOAdmin(BasePermission):
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


class EsDuenoFacturaOAdmin(BasePermission):
    """Solo lectura -- ver comentario en FacturaViewSet."""
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
        return str(obj.pago.cliente_id) == str(usuario.cliente_id)


class EsDuenoReembolsoOVerAdmin(BasePermission):
    """
    Cliente: puede crear/ver SOLO los reembolsos de sus propios pagos.
    Admin: puede ver, aprobar o rechazar cualquiera.
    La aprobacion/rechazo (update/partial_update) se restringe a admin
    dentro del ViewSet, no aqui.
    """
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
        return str(obj.pago.cliente_id) == str(usuario.cliente_id)