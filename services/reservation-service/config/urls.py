from django.urls import path, include

urlpatterns = [
    path('api/reservaciones/', include('reservations.urls')),
]