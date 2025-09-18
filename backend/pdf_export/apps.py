from django.apps import AppConfig

class PDFExportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdf_export'
    verbose_name = 'Export PDF'
    
    def ready(self):
        import pdf_export.signals
