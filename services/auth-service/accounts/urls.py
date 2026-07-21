from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuditoriaAccesoViewSet, ClienteViewSet, DireccionViewSet,
    LoginView, LogoutView, RefreshView, UsuarioViewSet,
)

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuarios")
router.register("clientes", ClienteViewSet, basename="clientes")
router.register("direcciones", DireccionViewSet, basename="direcciones")
router.register("auditoria-accesos", AuditoriaAccesoViewSet, basename="auditoria-accesos")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", RefreshView.as_view(), name="login-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
