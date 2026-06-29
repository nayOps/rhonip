"""
Vues API biométrique ONIP — matricule RH (registration_number).
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .permissions import GuichetInternalOrAuthenticated
from .serializers import BiometricDataSerializer, FingerprintCaptureSerializer
from apps.biometric.models import BiometricData, FingerprintCapture


class BiometricDataViewSet(viewsets.ModelViewSet):
    queryset = BiometricData.objects.all()
    serializer_class = BiometricDataSerializer
    permission_classes = [GuichetInternalOrAuthenticated]
    lookup_field = 'registration_number'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        matricule = data['registration_number']
        obj, _created = BiometricData.objects.update_or_create(
            registration_number=matricule,
            defaults={k: v for k, v in data.items() if k != 'registration_number'},
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


class FingerprintCaptureViewSet(viewsets.ModelViewSet):
    queryset = FingerprintCapture.objects.all()
    serializer_class = FingerprintCaptureSerializer
    permission_classes = [GuichetInternalOrAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        obj, _created = FingerprintCapture.objects.update_or_create(
            registration_number=data['registration_number'],
            finger_position=data['finger_position'],
            defaults={
                k: v
                for k, v in data.items()
                if k not in ('registration_number', 'finger_position')
            },
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)


def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'ONIP Biometric Core', 'version': '2.0.0'})


@api_view(['GET'])
@permission_classes([GuichetInternalOrAuthenticated])
def get_biometric_by_matricule(request, registration_number):
    record = get_object_or_404(BiometricData, registration_number=registration_number)
    return Response(BiometricDataSerializer(record).data)
