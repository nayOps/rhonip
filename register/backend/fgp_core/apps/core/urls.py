"""
URLs API biométrique ONIP (matricule RH).
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'biometric', views.BiometricDataViewSet, basename='biometric')
router.register(r'fingerprints', views.FingerprintCaptureViewSet, basename='fingerprints')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health-check'),
    path(
        'biometric/by-matricule/<str:registration_number>/',
        views.get_biometric_by_matricule,
        name='get-biometric-by-matricule',
    ),
]
