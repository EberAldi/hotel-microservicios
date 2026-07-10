from django.urls import path, include

urlpatterns = [
    path('api/pagos/', include('payments.urls')),
]