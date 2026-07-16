from rest_framework.routers import DefaultRouter
from .views import (
    ReservacionViewSet, ReservacionServicioViewSet, HistorialEstadoReservacionViewSet,
    CarritoViewSet, CarritoItemViewSet,
)

router = DefaultRouter()
router.register('reservaciones', ReservacionViewSet, basename='reservacion')
router.register('reservacion-servicios', ReservacionServicioViewSet, basename='reservacion-servicio')
router.register('historial-estados-reservacion', HistorialEstadoReservacionViewSet, basename='historial-estado-reservacion')
router.register('carritos', CarritoViewSet, basename='carrito')
router.register('carrito-items', CarritoItemViewSet, basename='carrito-item')

urlpatterns = router.urls