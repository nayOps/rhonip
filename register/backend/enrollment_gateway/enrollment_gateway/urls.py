"""
URL configuration for Enrollment Gateway service.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.enrollment.views import dashboard_stats

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/v1/enrolments/', include('apps.enrollment.urls')),
    path('api/v1/dashboard/stats/', dashboard_stats, name='dashboard-stats-root'),
    path('api/v1/validation/', include('apps.validation.urls')),
    path('api/v1/orchestration/', include('apps.orchestration.urls')),
    path('api/v1/notifications/', include('apps.notification.urls')),
    
    # Health check
    path('health/', include('apps.enrollment.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
