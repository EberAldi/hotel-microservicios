from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet, ClienteViewSet

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')
router.register('clientes', ClienteViewSet, basename='cliente')

urlpatterns = router.urls