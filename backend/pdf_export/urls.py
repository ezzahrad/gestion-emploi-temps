from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PDFTemplateViewSet, PDFExportJobViewSet, PDFExportViewSet,
    PDFExportSettingsViewSet, PDFExportStatisticsViewSet
)

router = DefaultRouter()
router.register(r'templates', PDFTemplateViewSet)
router.register(r'jobs', PDFExportJobViewSet)
router.register(r'settings', PDFExportSettingsViewSet)
router.register(r'statistics', PDFExportStatisticsViewSet)

# URLs pour les exports (pas de CRUD complet)
export_patterns = [
    path('create/', PDFExportViewSet.as_view({'post': 'create_export'}), name='create-export'),
    path('bulk/', PDFExportViewSet.as_view({'post': 'bulk_export'}), name='bulk-export'),
    path('types/', PDFExportViewSet.as_view({'get': 'available_types'}), name='available-types'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('export/', include(export_patterns)),
]
