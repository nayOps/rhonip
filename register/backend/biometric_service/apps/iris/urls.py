"""
URL configuration pour l'API Iris
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IrisCaptureSessionViewSet,
    IrisCaptureViewSet,
    IrisTemplateViewSet,
    IrisMatchViewSet,
)

router = DefaultRouter()
router.register(r'sessions', IrisCaptureSessionViewSet, basename='iris-session')
router.register(r'captures', IrisCaptureViewSet, basename='iris-capture')
router.register(r'templates', IrisTemplateViewSet, basename='iris-template')
router.register(r'matches', IrisMatchViewSet, basename='iris-match')

urlpatterns = [
    path('', include(router.urls)),
]

