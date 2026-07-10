from django.urls import path, include

urlpatterns = [
    path('api/catalogo/', include('rooms.urls')),
    path('api/catalogo/', include('services_catalog.urls')),
]