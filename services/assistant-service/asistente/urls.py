from django.urls import path
from .views import ClimaView, ChatView

urlpatterns = [
    path('clima/', ClimaView.as_view(), name='clima'),
    path('chat/', ChatView.as_view(), name='chat'),
]