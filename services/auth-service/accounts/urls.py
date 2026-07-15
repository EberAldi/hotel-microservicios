from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UsuarioViewSet, ClienteViewSet, DireccionViewSet, AuditoriaAccesoViewSet,
    LoginView, RefreshView, LogoutView,
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')
router.register('clientes', ClienteViewSet, basename='cliente')
router.register('direcciones', DireccionViewSet, basename='direccion')
router.register('auditoria-accesos', AuditoriaAccesoViewSet, basename='auditoria-acceso')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', RefreshView.as_view(), name='login-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
] + router.urls