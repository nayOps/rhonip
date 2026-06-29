#!/bin/bash
docker exec onip_rh_server python /app/backend/manage.py shell -c "
from django.conf import settings
print('DEBUG', settings.DEBUG)
print('CSRF_COOKIE_SECURE', settings.CSRF_COOKIE_SECURE)
print('SESSION_COOKIE_SECURE', settings.SESSION_COOKIE_SECURE)
print('CSRF_TRUSTED_ORIGINS', settings.CSRF_TRUSTED_ORIGINS)
print('ALLOWED_HOSTS', settings.ALLOWED_HOSTS)
"
