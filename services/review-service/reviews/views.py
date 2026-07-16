from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Resena, RespuestaResena
from .serializers import ResenaSerializer, RespuestaResenaSerializer
from .permissions import EsClienteOAdmin, EsDuenoResenaOAdmin, EsAdmin, EsDuenoRespuestaOAdmin


class ResenaViewSet(viewsets.ModelViewSet):
    """
    GET: publico. Invitados y clientes ven SOLO 'aprobada'. Admin ve todas
    (y puede filtrar por estado).
    POST: requiere JWT cliente/admin. Se crea SIEMPRE en 'aprobada'
    (moderacion reactiva), 'estado' no se puede mandar en el body.
    PUT/PATCH/DELETE: solo el dueño (contenido/calificacion) o admin.
    Cambiar 'estado' (ocultar/aprobar) se hace SOLO via /moderar/, solo admin.

    Filtros opcionales por query param:
      /api/resenas/resenas/?tipo_objetivo=HABITACION&objetivo_id=<uuid>
      /api/resenas/resenas/?cliente_id=<uuid>
      /api/resenas/resenas/?estado=oculta   (solo tiene efecto para admin)
    """
    serializer_class = ResenaSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        if self.action == 'create':
            return [EsClienteOAdmin()]
        if self.action == 'moderar':
            return [EsAdmin()]
        return [EsDuenoResenaOAdmin()]

    def get_queryset(self):
        queryset = Resena.objects.all().order_by('-id')
        usuario = getattr(self.request, 'user', None)
        es_admin = bool(usuario and getattr(usuario, 'is_authenticated', False) and usuario.rol == 'admin')

        if not es_admin:
            queryset = queryset.filter(estado='aprobada')
        else:
            estado = self.request.query_params.get('estado')
            if estado:
                queryset = queryset.filter(estado=estado)

        tipo_objetivo = self.request.query_params.get('tipo_objetivo')
        objetivo_id = self.request.query_params.get('objetivo_id')
        cliente_id = self.request.query_params.get('cliente_id')
        if tipo_objetivo:
            queryset = queryset.filter(tipo_objetivo=tipo_objetivo)
        if objetivo_id:
            queryset = queryset.filter(objetivo_id=objetivo_id)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.rol == 'cliente':
            serializer.save(cliente_id=usuario.cliente_id, estado='aprobada')
        else:
            cliente_id = self.request.data.get('cliente_id')
            if not cliente_id:
                raise PermissionDenied('Como admin, debes indicar cliente_id en el body.')
            serializer.save(cliente_id=cliente_id, estado='aprobada')

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Reseña eliminada correctamente'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='moderar')
    def moderar(self, request, pk=None):
        """
        POST /api/resenas/resenas/{id}/moderar/   body: {"estado": "oculta"}
        Solo admin. Unica forma de ocultar/reaprobar una resena.
        """
        estado_nuevo = request.data.get('estado')
        if estado_nuevo not in ('aprobada', 'oculta'):
            return Response({'detail': "estado debe ser 'aprobada' u 'oculta'."}, status=400)
        resena = self.get_object()
        resena.estado = estado_nuevo
        resena.save(update_fields=['estado'])
        return Response({'mensaje': f'Reseña marcada como {estado_nuevo}'}, status=200)


class RespuestaResenaViewSet(viewsets.ModelViewSet):
    """
    GET: publico (no requiere token).
    POST: requiere JWT cliente/admin. autor_tipo/autor_id se asignan
    automaticamente desde el token, nunca se mandan en el body.
    PUT/PATCH/DELETE: solo el autor de la respuesta o admin.
    """
    serializer_class = RespuestaResenaSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        if self.action == 'create':
            return [EsClienteOAdmin()]
        return [EsDuenoRespuestaOAdmin()]

    def get_queryset(self):
        queryset = RespuestaResena.objects.select_related('resena').all()
        resena_id = self.request.query_params.get('resena_id')
        if resena_id:
            queryset = queryset.filter(resena_id=resena_id)
        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.rol == 'admin':
            serializer.save(autor_tipo='admin', autor_id=usuario.id)
        else:
            serializer.save(autor_tipo='cliente', autor_id=usuario.cliente_id)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({'mensaje': 'Respuesta modificada correctamente'}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        return Response({'mensaje': 'Respuesta modificada correctamente'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'mensaje': 'Respuesta eliminada correctamente'}, status=status.HTTP_200_OK)