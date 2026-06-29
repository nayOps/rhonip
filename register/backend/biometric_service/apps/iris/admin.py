"""
Admin configuration for Iris models
"""

from django.contrib import admin
from .models import (
    IrisCaptureSession,
    IrisCapture,
    IrisTemplate,
    IrisMatch,
    IrisQualityLog
)


@admin.register(IrisCaptureSession)
class IrisCaptureSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'enrollment_session_id', 'status', 'started_at', 'operator_id']
    list_filter = ['status', 'started_at']
    search_fields = ['id', 'enrollment_session_id', 'operator_id']
    readonly_fields = ['id', 'started_at', 'completed_at']


@admin.register(IrisCapture)
class IrisCaptureAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'eye_position', 'status', 'quality_score', 'is_valid', 'captured_at']
    list_filter = ['status', 'eye_position', 'is_valid', 'captured_at']
    search_fields = ['id', 'session__id']
    readonly_fields = ['id', 'captured_at', 'processed_at']


@admin.register(IrisTemplate)
class IrisTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'capture', 'encoding_method', 'template_size', 'created_at']
    list_filter = ['encoding_method', 'created_at']
    search_fields = ['id', 'capture__id']
    readonly_fields = ['id', 'created_at', 'template_size']


@admin.register(IrisMatch)
class IrisMatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_match', 'similarity_score', 'matched_at']
    list_filter = ['is_match', 'matched_at']
    readonly_fields = ['id', 'matched_at']


@admin.register(IrisQualityLog)
class IrisQualityLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'capture', 'overall_score', 'pupil_detected', 'iris_detected', 'created_at']
    list_filter = ['pupil_detected', 'iris_detected', 'created_at']
    search_fields = ['id', 'capture__id']
    readonly_fields = ['id', 'created_at']

