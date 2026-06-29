"""
Configuration Celery pour Enrollment Gateway.
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enrollment_gateway.settings')

app = Celery('enrollment_gateway')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

