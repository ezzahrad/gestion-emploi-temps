from django.apps import AppConfig

class AbsencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'absences'
    verbose_name = 'Gestion des Absences'
    
    def ready(self):
        import absences.signals
