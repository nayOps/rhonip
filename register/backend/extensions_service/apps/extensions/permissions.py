"""Permissions — accès interne guichet (service-to-service)."""
from django.conf import settings
from rest_framework.permissions import BasePermission


class GuichetInternalOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        expected = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
        if expected and request.headers.get('X-Guichet-Internal-Key') == expected:
            return True
        return bool(request.user and request.user.is_authenticated)
