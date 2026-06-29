from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('fingerprint/open/', views.open_device, name='fingerprint-open'),
    path('fingerprint/close/', views.close_device, name='fingerprint-close'),
    path('fingerprint/capture/', views.capture, name='fingerprint-capture'),
]
