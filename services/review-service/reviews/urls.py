from rest_framework.routers import DefaultRouter

from .views import ResenaViewSet, RespuestaResenaViewSet

router = DefaultRouter()
router.register('resenas', ResenaViewSet, basename='resena')
router.register('respuestas-resena', RespuestaResenaViewSet, basename='respuesta-resena')

urlpatterns = router.urls