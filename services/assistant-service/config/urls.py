from django.urls import path, include

urlpatterns = [
    path('api/asistente/', include('asistente.urls')),
]