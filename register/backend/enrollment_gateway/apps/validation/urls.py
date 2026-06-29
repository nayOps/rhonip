"""
URLs pour l'application Validation
"""
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check pour le service de validation"""
    return Response({
        'status': 'healthy',
        'service': 'Validation Service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('health/', health_check, name='health-check'),
]
