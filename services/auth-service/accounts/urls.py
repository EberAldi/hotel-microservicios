from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UsuarioViewSet, ClienteViewSet, LoginView

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')
router.register('clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
] + router.urls