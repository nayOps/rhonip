from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExtensionEducationViewSet, ExtensionElectoralViewSet, ExtensionPNCViewSet,
    ExtensionFARDCViewSet, ExtensionPrisonViewSet, ExtensionRefugieViewSet,
    ExtensionEnfantViewSet, ExtensionFonctionnaireViewSet, ExtensionManagerViewSet
)

router = DefaultRouter()
router.register(r'education', ExtensionEducationViewSet, basename='ext-education')
router.register(r'electoral', ExtensionElectoralViewSet, basename='ext-electoral')
router.register(r'pnc', ExtensionPNCViewSet, basename='ext-pnc')
router.register(r'fardc', ExtensionFARDCViewSet, basename='ext-fardc')
router.register(r'prison', ExtensionPrisonViewSet, basename='ext-prison')
router.register(r'refugee', ExtensionRefugieViewSet, basename='ext-refugee')
router.register(r'enfant', ExtensionEnfantViewSet, basename='ext-enfant')
router.register(r'fonctionnaire', ExtensionFonctionnaireViewSet, basename='ext-fonctionnaire')

urlpatterns = [
    path('', include(router.urls)),
    path('manage/create-multiple/', ExtensionManagerViewSet.as_view({'post': 'create_multiple'}), name='ext-create-multiple'),
    path('manage/search/', ExtensionManagerViewSet.as_view({'get': 'search'}), name='ext-search'),
    path('manage/stats/', ExtensionManagerViewSet.as_view({'get': 'global_stats'}), name='ext-global-stats'),
]


