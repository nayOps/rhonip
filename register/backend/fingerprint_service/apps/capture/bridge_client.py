import requests
from django.conf import settings


class DeviceBridgeError(Exception):
    pass


class DeviceBridgeClient:
    def __init__(self):
        self.base_url = settings.DEVICE_BRIDGE_URL.rstrip('/')
        self.timeout = settings.DEVICE_BRIDGE_TIMEOUT

    def health(self):
        return self._get('/health')

    def open_fingerprint(self):
        return self._post('/api/v1/devices/fingerprint/open')

    def close_fingerprint(self):
        return self._post('/api/v1/devices/fingerprint/close')

    def capture_fingerprint(self, payload: dict):
        return self._post('/api/v1/devices/fingerprint/capture', json=payload)

    def _get(self, path: str):
        try:
            r = requests.get(f'{self.base_url}{path}', timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise DeviceBridgeError(str(e)) from e

    def _post(self, path: str, json: dict | None = None):
        try:
            r = requests.post(f'{self.base_url}{path}', json=json or {}, timeout=self.timeout)
            if r.status_code >= 400:
                try:
                    body = r.json()
                except ValueError:
                    body = {'message': r.text}
                raise DeviceBridgeError(body.get('message', r.text))
            return r.json()
        except requests.RequestException as e:
            raise DeviceBridgeError(str(e)) from e
