from rest_framework.routers import DefaultRouter
from .views import ReservacionViewSet, ReservacionServicioViewSet

router = DefaultRouter()
router.register('reservaciones', ReservacionViewSet, basename='reservacion')
router.register('reservacion-servicios', ReservacionServicioViewSet, basename='reservacion-servicio')

urlpatterns = router.urls