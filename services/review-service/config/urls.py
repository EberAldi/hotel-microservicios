from django.urls import path, include

urlpatterns = [
    path('api/resenas/', include('reviews.urls')),
]