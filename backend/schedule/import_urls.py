from django.urls import path
from . import import_export_views

urlpatterns = [
    # Import Excel - URL attendue par le frontend
    path('', import_export_views.import_schedules, name='import_excel'),
    path('template/', import_export_views.download_import_template, name='download_template'),
]
