"""
WSGI config for FGP Core service.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fgp_core.settings')

application = get_wsgi_application()
