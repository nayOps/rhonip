"""
Permissions FGP Core — accès interne guichet (service-to-service).
"""
from django.conf import settings
from rest_framework.permissions import BasePermission


class GuichetInternalOrAuthenticated(BasePermission):
    """
    Autorise la création de personne via clé interne (enrollment_gateway/worker),
    sinon authentification JWT classique.
    """

    def has_permission(self, request, view):
        expected = getattr(settings, 'GUICHET_INTERNAL_API_KEY', None)
        if (
            expected
            and request.headers.get('X-Guichet-Internal-Key') == expected
            and getattr(view, 'action', None) == 'create'
        ):
            return True
        return bool(request.user and request.user.is_authenticated)
