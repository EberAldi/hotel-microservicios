from rest_framework.routers import DefaultRouter
from .views import PagoViewSet, FacturaViewSet, ReembolsoViewSet

router = DefaultRouter()
router.register('pagos', PagoViewSet, basename='pago')
router.register('facturas', FacturaViewSet, basename='factura')
router.register('reembolsos', ReembolsoViewSet, basename='reembolso')

urlpatterns = router.urls