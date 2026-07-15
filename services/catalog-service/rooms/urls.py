from rest_framework.routers import DefaultRouter
from .views import TipoHabitacionViewSet, HabitacionViewSet, ImagenHabitacionViewSet, DisponibilidadHabitacionViewSet

router = DefaultRouter()
router.register('tipos-habitacion', TipoHabitacionViewSet, basename='tipo-habitacion')
router.register('habitaciones', HabitacionViewSet, basename='habitacion')
router.register('imagenes-habitacion', ImagenHabitacionViewSet, basename='imagen-habitacion')
router.register('disponibilidad-habitacion', DisponibilidadHabitacionViewSet, basename='disponibilidad-habitacion')

urlpatterns = router.urls