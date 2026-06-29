"""
URLs pour l'application Enrollment
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.EnrollmentSessionViewSet)
router.register(r'validations', views.EnrollmentValidationViewSet)
router.register(r'events', views.EnrollmentEventViewSet)
router.register(r'receipts', views.EnrollmentReceiptViewSet)
router.register(r'stats', views.EnrollmentStatsViewSet, basename='stats')

urlpatterns = [
    # API Endpoints
    path('', include(router.urls)),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
    
    # Endpoints spécifiques
    path('sessions/status/<str:session_id>/', views.EnrollmentSessionViewSet.as_view({'get': 'get_status'}), name='session-status'),
    path('sessions/cancel/<str:session_id>/', views.EnrollmentSessionViewSet.as_view({'post': 'cancel_session'}), name='cancel-session'),
    path('sessions/search/', views.EnrollmentSessionViewSet.as_view({'post': 'search'}), name='search-sessions'),
    path('receipts/by-matricule/<str:registration_number>/', views.EnrollmentReceiptViewSet.as_view({'get': 'get_by_matricule'}), name='receipt-by-matricule'),
    path('stats/daily/', views.EnrollmentStatsViewSet.as_view({'get': 'get_stats'}), name='daily-stats'),
    # Dashboard stats
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]
