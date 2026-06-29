from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .bridge_client import DeviceBridgeClient, DeviceBridgeError


@api_view(['GET'])
def health(request):
    client = DeviceBridgeClient()
    try:
        data = client.health()
        return Response({'bridge': data, 'service': 'fingerprint_service', 'status': 'ok'})
    except DeviceBridgeError as e:
        return Response(
            {'bridge': None, 'service': 'fingerprint_service', 'status': 'degraded', 'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(['POST'])
def open_device(request):
    try:
        return Response(DeviceBridgeClient().open_fingerprint())
    except DeviceBridgeError as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def close_device(request):
    try:
        return Response(DeviceBridgeClient().close_fingerprint())
    except DeviceBridgeError as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
def capture(request):
    payload = {
        'capture_type': request.data.get('capture_type', 'left_four'),
        'finger_position': request.data.get('finger_position'),
        'present_fingers': request.data.get('present_fingers'),
        'missing_fingers': request.data.get('missing_fingers', 0),
        'timeout_ms': request.data.get('timeout_ms', 30000),
        'template_format': request.data.get('template_format', 4),
        'nfiq_threshold': request.data.get('nfiq_threshold', 3),
    }
    if payload.get('finger_position'):
        payload['capture_type'] = 'single'

    try:
        result = DeviceBridgeClient().capture_fingerprint(payload)
        status_code = status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    except DeviceBridgeError as e:
        return Response(
            {
                'success': False,
                'message': f'Bridge inaccessible ({settings.DEVICE_BRIDGE_URL}): {e}',
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
