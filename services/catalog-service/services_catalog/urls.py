from rest_framework.routers import DefaultRouter
from .views import CategoriaServicioViewSet, ServicioViewSet, ImagenServicioViewSet

router = DefaultRouter()
router.register('categorias-servicio', CategoriaServicioViewSet, basename='categoria-servicio')
router.register('servicios', ServicioViewSet, basename='servicio')
router.register('imagenes-servicio', ImagenServicioViewSet, basename='imagen-servicio')

urlpatterns = router.urls