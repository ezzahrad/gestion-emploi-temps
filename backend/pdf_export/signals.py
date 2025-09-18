from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import PDFExportJob, PDFExportStatistics
from notifications.models import Notification
import os

@receiver(post_save, sender=PDFExportJob)
def handle_pdf_export_completion(sender, instance, **kwargs):
    """Gérer la finalisation d'un export PDF"""
    if instance.status == 'completed':
        # Créer une notification pour l'utilisateur
        Notification.objects.create(
            recipient=instance.requested_by,
            title="Export PDF terminé",
            message=f"Votre export {instance.get_export_type_display()} est prêt à être téléchargé.",
            notification_type='system',
            priority='medium',
            metadata={
                'export_job_id': str(instance.job_id),
                'download_url': instance.get_download_url(),
                'file_size': instance.get_file_size_display(),
                'page_count': instance.page_count
            }
        )
        
        # Mettre à jour les statistiques
        update_daily_statistics(instance)
        
    elif instance.status == 'failed':
        # Notifier l'échec
        Notification.objects.create(
            recipient=instance.requested_by,
            title="Échec de l'export PDF",
            message=f"L'export {instance.get_export_type_display()} a échoué: {instance.error_message}",
            notification_type='system',
            priority='high',
            metadata={
                'export_job_id': str(instance.job_id),
                'error_message': instance.error_message
            }
        )

@receiver(post_delete, sender=PDFExportJob)
def cleanup_pdf_file(sender, instance, **kwargs):
    """Nettoyer le fichier PDF lors de la suppression du job"""
    if instance.file_path and os.path.exists(instance.file_path):
        try:
            os.remove(instance.file_path)
        except OSError:
            pass  # Fichier déjà supprimé ou erreur d'accès

def update_daily_statistics(export_job):
    """Mettre à jour les statistiques quotidiennes"""
    today = timezone.now().date()
    stats, created = PDFExportStatistics.objects.get_or_create(date=today)
    
    # Incrémenter les compteurs
    stats.total_exports += 1
    
    if export_job.status == 'completed':
        stats.successful_exports += 1
        
        # Ajouter la taille du fichier
        if export_job.file_size:
            file_size_mb = export_job.file_size / (1024 * 1024)
            stats.total_file_size_mb += file_size_mb
        
        # Ajouter le nombre de pages
        if export_job.page_count:
            stats.total_pages_generated += export_job.page_count
        
        # Calculer le temps de traitement
        if export_job.started_at and export_job.completed_at:
            processing_time = (export_job.completed_at - export_job.started_at).total_seconds()
            # Moyenne pondérée du temps de traitement
            current_avg = float(stats.average_processing_time_seconds)
            new_avg = ((current_avg * (stats.successful_exports - 1)) + processing_time) / stats.successful_exports
            stats.average_processing_time_seconds = new_avg
        
        # Incrémenter les compteurs par type
        if export_job.export_type in ['schedule', 'teacher_schedule', 'room_schedule']:
            stats.schedule_exports += 1
        elif export_job.export_type in ['transcript', 'bulk_transcripts']:
            stats.transcript_exports += 1
        elif export_job.export_type in ['absence_report', 'attendance_report']:
            stats.report_exports += 1
            
    elif export_job.status == 'failed':
        stats.failed_exports += 1
    
    stats.save()
