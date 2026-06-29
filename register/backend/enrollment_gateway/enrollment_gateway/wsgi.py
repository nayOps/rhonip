"""
WSGI config for Enrollment Gateway service.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enrollment_gateway.settings')

application = get_wsgi_application()
