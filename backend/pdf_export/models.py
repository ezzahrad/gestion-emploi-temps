from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()

class PDFTemplate(models.Model):
    """Templates pour la génération de PDF"""
    TEMPLATE_TYPE_CHOICES = (
        ('schedule', 'Emploi du temps'),
        ('transcript', 'Relevé de notes'),
        ('absence_report', 'Rapport d\'absences'),
        ('attendance_report', 'Rapport de présences'),
        ('student_card', 'Carte étudiant'),
        ('teacher_schedule', 'Planning enseignant'),
        ('room_schedule', 'Planning salle'),
        ('certificate', 'Certificat'),
        ('letter', 'Lettre officielle'),
    )
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Configuration du template
    page_format = models.CharField(max_length=10, default='A4', choices=[
        ('A3', 'A3'), ('A4', 'A4'), ('A5', 'A5'), ('Letter', 'Letter')
    ])
    orientation = models.CharField(max_length=10, default='portrait', choices=[
        ('portrait', 'Portrait'), ('landscape', 'Paysage')
    ])
    
    # Marges en mm
    margin_top = models.IntegerField(default=20)
    margin_bottom = models.IntegerField(default=20)
    margin_left = models.IntegerField(default=20)
    margin_right = models.IntegerField(default=20)
    
    # Styles
    header_template = models.TextField(blank=True, help_text="Template HTML pour l'en-tête")
    footer_template = models.TextField(blank=True, help_text="Template HTML pour le pied de page")
    css_styles = models.TextField(blank=True, help_text="Styles CSS personnalisés")
    
    # Métadonnées
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def save(self, *args, **kwargs):
        if self.is_default:
            # S'assurer qu'il n'y a qu'un seul template par défaut par type
            PDFTemplate.objects.filter(
                template_type=self.template_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

class PDFExportJob(models.Model):
    """Suivi des tâches de génération PDF"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    )
    
    EXPORT_TYPE_CHOICES = (
        ('schedule', 'Emploi du temps'),
        ('transcript', 'Relevé de notes'),
        ('absence_report', 'Rapport d\'absences'),
        ('attendance_report', 'Rapport de présences'),
        ('bulk_schedules', 'Emplois du temps en masse'),
        ('bulk_transcripts', 'Relevés en masse'),
    )
    
    # Identifiant unique
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Détails de l'export
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    template = models.ForeignKey(PDFTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Statut et progression
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, help_text="Progression en pourcentage")
    
    # Paramètres de l'export (JSON)
    export_parameters = models.JSONField(default=dict)
    
    # Résultats
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, help_text="Taille en bytes")
    page_count = models.IntegerField(null=True, blank=True)
    
    # Messages et erreurs
    success_message = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_exports')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_export_type_display()} - {self.status} ({self.progress}%)"

    def get_download_url(self):
        """Obtenir l'URL de téléchargement"""
        if self.status == 'completed' and self.file_path:
            return f"/api/pdf-export/download/{self.job_id}/"
        return None

    def get_file_size_display(self):
        """Afficher la taille du fichier de manière lisible"""
        if not self.file_size:
            return "N/A"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def mark_as_processing(self):
        """Marquer comme en cours de traitement"""
        from django.utils import timezone
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_as_completed(self, file_path, file_size=None, page_count=None, message=""):
        """Marquer comme terminé"""
        from django.utils import timezone
        self.status = 'completed'
        self.progress = 100
        self.file_path = file_path
        self.file_size = file_size
        self.page_count = page_count
        self.success_message = message
        self.completed_at = timezone.now()
        # Expiration dans 7 jours
        self.expires_at = timezone.now() + timezone.timedelta(days=7)
        self.save()

    def mark_as_failed(self, error_message, error_details=None):
        """Marquer comme échoué"""
        from django.utils import timezone
        self.status = 'failed'
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
        self.completed_at = timezone.now()
        self.save()

class PDFExportSettings(models.Model):
    """Configuration globale pour l'export PDF"""
    # Répertoires
    output_directory = models.CharField(max_length=500, default='pdf_exports/')
    temp_directory = models.CharField(max_length=500, default='pdf_temp/')
    
    # Limites
    max_file_size_mb = models.IntegerField(default=50, help_text="Taille max en MB")
    max_pages_per_document = models.IntegerField(default=500)
    max_concurrent_jobs = models.IntegerField(default=5)
    job_retention_days = models.IntegerField(default=7, help_text="Durée de conservation des fichiers")
    
    # Qualité et performance
    image_quality = models.IntegerField(default=85, help_text="Qualité des images (1-100)")
    compression_level = models.IntegerField(default=6, help_text="Niveau de compression (1-9)")
    enable_parallelization = models.BooleanField(default=True)
    
    # Watermark
    enable_watermark = models.BooleanField(default=False)
    watermark_text = models.CharField(max_length=200, blank=True)
    watermark_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.1)
    
    # Email notifications
    send_completion_email = models.BooleanField(default=True)
    admin_notification_email = models.EmailField(blank=True)
    
    # Sécurité
    require_authentication = models.BooleanField(default=True)
    allow_public_downloads = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration PDF Export"
        verbose_name_plural = "Configurations PDF Export"

    def __str__(self):
        return f"Configuration PDF Export - {self.updated_at.strftime('%d/%m/%Y')}"

class PDFExportStatistics(models.Model):
    """Statistiques d'utilisation des exports PDF"""
    date = models.DateField(unique=True)
    
    # Compteurs par type
    total_exports = models.IntegerField(default=0)
    successful_exports = models.IntegerField(default=0)
    failed_exports = models.IntegerField(default=0)
    
    # Par type d'export
    schedule_exports = models.IntegerField(default=0)
    transcript_exports = models.IntegerField(default=0)
    report_exports = models.IntegerField(default=0)
    
    # Volumes
    total_file_size_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pages_generated = models.IntegerField(default=0)
    
    # Performance
    average_processing_time_seconds = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    peak_concurrent_jobs = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Statistiques PDF Export"
        verbose_name_plural = "Statistiques PDF Export"

    def __str__(self):
        return f"Stats {self.date.strftime('%d/%m/%Y')} - {self.total_exports} exports"

class PDFDownloadLog(models.Model):
    """Log des téléchargements de PDF"""
    export_job = models.ForeignKey(PDFExportJob, on_delete=models.CASCADE, related_name='download_logs')
    downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_downloads')
    
    # Détails du téléchargement
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    download_successful = models.BooleanField(default=True)
    bytes_transferred = models.BigIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Téléchargement par {self.downloaded_by.full_name} - {self.created_at}"
