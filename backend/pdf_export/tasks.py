"""
Tâches Celery pour la génération et traitement des PDF
"""

import os
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from io import BytesIO

# Import conditionnel de ReportLab
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, A3, letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from .models import PDFExportJob, PDFExportSettings
from .pdf_generators import (
    SchedulePDFGenerator, 
    TranscriptPDFGenerator, 
    AbsenceReportPDFGenerator,
    BulkExportPDFGenerator,
    PDFGeneratorFactory
)

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_pdf_export(self, job_id: int, export_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tâche principale pour traiter un export PDF
    
    Args:
        job_id: ID du job d'export
        export_data: Données de configuration de l'export
    
    Returns:
        Dict avec les résultats de l'export
    """
    
    if not REPORTLAB_AVAILABLE:
        logger.error("ReportLab non disponible pour la génération PDF")
        return {
            'success': False,
            'error': 'ReportLab non installé. Exécutez: pip install reportlab'
        }
    
    try:
        # Récupérer le job
        job = PDFExportJob.objects.get(job_id=job_id)
        job.status = 'processing'
        job.progress = 10
        job.save()
        
        # Récupérer les paramètres
        settings_obj = PDFExportSettings.get_settings()
        
        # Créer le répertoire de sortie si nécessaire
        output_dir = getattr(settings, 'MEDIA_ROOT', 'media') + '/' + settings_obj.output_directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Sélectionner le générateur approprié
        generator = get_pdf_generator(export_data['export_type'])
        if not generator:
            raise ValueError(f"Type d'export non supporté: {export_data['export_type']}")
        
        job.progress = 30
        job.save()
        
        # Générer le PDF
        pdf_result = generator.generate(export_data, job)
        
        job.progress = 80
        job.save()
        
        # Sauvegarder le fichier
        if pdf_result['success']:
            # Construire le chemin du fichier
            filename = f"{export_data['export_type']}_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path = os.path.join(output_dir, filename)
            
            # Écrire le fichier
            with open(file_path, 'wb') as f:
                f.write(pdf_result['pdf_data'])
            
            # Mettre à jour le job
            job.status = 'completed'
            job.progress = 100
            job.file_path = file_path
            job.file_size = len(pdf_result['pdf_data'])
            job.file_size_display = format_file_size(len(pdf_result['pdf_data']))
            job.page_count = pdf_result.get('page_count', 0)
            job.processing_time = pdf_result.get('processing_time', 0)
            job.success_message = f"PDF généré avec succès: {filename}"
            job.download_url = f"/media/{settings_obj.output_directory}{filename}"
            job.save()
            
            # Programmer le nettoyage
            schedule_cleanup.apply_async(
                args=[job_id], 
                countdown=settings_obj.job_retention_days * 24 * 60 * 60
            )
            
            # Envoyer une notification (optionnel)
            send_export_notification.delay(job.created_by.id, job_id, 'completed')
            
            logger.info(f"Export PDF réussi pour job {job_id}: {filename}")
            
            return {
                'success': True,
                'job_id': job_id,
                'filename': filename,
                'file_size': job.file_size,
                'page_count': job.page_count
            }
        else:
            raise Exception(pdf_result.get('error', 'Erreur inconnue lors de la génération PDF'))
            
    except PDFExportJob.DoesNotExist:
        logger.error(f"Job PDF non trouvé: {job_id}")
        return {'success': False, 'error': f'Job {job_id} non trouvé'}
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'export PDF {job_id}: {str(exc)}")
        
        try:
            job = PDFExportJob.objects.get(job_id=job_id)
            job.status = 'failed'
            job.error_message = str(exc)
            job.save()
            
            # Envoyer une notification d'erreur
            send_export_notification.delay(job.created_by.id, job_id, 'failed')
            
        except PDFExportJob.DoesNotExist:
            pass
        
        # Retry avec backoff exponentiel
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            raise self.retry(countdown=countdown, exc=exc)
        
        return {
            'success': False,
            'error': str(exc),
            'job_id': job_id
        }


@shared_task
def process_bulk_export(job_ids: list, bulk_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traiter plusieurs exports PDF en parallèle
    
    Args:
        job_ids: Liste des IDs de jobs à traiter
        bulk_settings: Paramètres pour l'export en masse
    
    Returns:
        Dict avec les résultats de l'export en masse
    """
    
    results = {
        'total_jobs': len(job_ids),
        'successful': 0,
        'failed': 0,
        'job_results': []
    }
    
    try:
        # Traiter chaque job
        for job_id in job_ids:
            try:
                job = PDFExportJob.objects.get(job_id=job_id)
                export_data = {
                    'export_type': job.export_type,
                    'parameters': job.parameters
                }
                
                # Traiter le job
                result = process_pdf_export.delay(job_id, export_data)
                job_result = result.get(timeout=300)  # Timeout de 5 minutes
                
                results['job_results'].append({
                    'job_id': job_id,
                    'success': job_result.get('success', False),
                    'filename': job_result.get('filename'),
                    'error': job_result.get('error')
                })
                
                if job_result.get('success'):
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Erreur traitement bulk job {job_id}: {str(e)}")
                results['failed'] += 1
                results['job_results'].append({
                    'job_id': job_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Créer un fichier ZIP si demandé
        if bulk_settings.get('create_zip', False) and results['successful'] > 0:
            zip_result = create_bulk_zip(results['job_results'], bulk_settings)
            results['zip_file'] = zip_result
        
        logger.info(f"Export en masse terminé: {results['successful']}/{results['total_jobs']} réussis")
        
    except Exception as exc:
        logger.error(f"Erreur lors de l'export en masse: {str(exc)}")
        results['error'] = str(exc)
    
    return results


@shared_task
def schedule_cleanup(job_id: int):
    """
    Nettoyer un job PDF expiré
    
    Args:
        job_id: ID du job à nettoyer
    """
    
    try:
        job = PDFExportJob.objects.get(job_id=job_id)
        
        # Supprimer le fichier
        if job.file_path and os.path.exists(job.file_path):
            os.remove(job.file_path)
            logger.info(f"Fichier PDF supprimé: {job.file_path}")
        
        # Marquer le job comme expiré
        job.status = 'expired'
        job.file_path = None
        job.download_url = None
        job.save()
        
    except PDFExportJob.DoesNotExist:
        logger.warning(f"Job à nettoyer non trouvé: {job_id}")
    except Exception as exc:
        logger.error(f"Erreur lors du nettoyage {job_id}: {str(exc)}")


@shared_task
def cleanup_expired_jobs():
    """
    Nettoyer tous les jobs PDF expirés
    Tâche à exécuter périodiquement via celery beat
    """
    
    try:
        settings_obj = PDFExportSettings.get_settings()
        expiration_date = timezone.now() - timedelta(days=settings_obj.job_retention_days)
        
        # Trouver les jobs expirés
        expired_jobs = PDFExportJob.objects.filter(
            created_at__lt=expiration_date,
            status__in=['completed', 'failed']
        )
        
        cleaned_count = 0
        for job in expired_jobs:
            try:
                # Supprimer le fichier
                if job.file_path and os.path.exists(job.file_path):
                    os.remove(job.file_path)
                
                # Marquer comme expiré
                job.status = 'expired'
                job.file_path = None
                job.download_url = None
                job.save()
                
                cleaned_count += 1
                
            except Exception as e:
                logger.error(f"Erreur nettoyage job {job.job_id}: {str(e)}")
        
        logger.info(f"Nettoyage terminé: {cleaned_count} jobs supprimés")
        
        return {
            'success': True,
            'cleaned_jobs': cleaned_count
        }
        
    except Exception as exc:
        logger.error(f"Erreur lors du nettoyage périodique: {str(exc)}")
        return {
            'success': False,
            'error': str(exc)
        }


@shared_task
def send_export_notification(user_id: int, job_id: int, status: str):
    """
    Envoyer une notification à l'utilisateur sur le statut de l'export
    
    Args:
        user_id: ID de l'utilisateur
        job_id: ID du job
        status: Statut du job ('completed', 'failed')
    """
    
    try:
        from notifications.models import Notification
        
        user = User.objects.get(id=user_id)
        job = PDFExportJob.objects.get(job_id=job_id)
        
        if status == 'completed':
            title = "Export PDF terminé"
            message = f"Votre export '{job.export_type}' est prêt à être téléchargé."
            notification_type = 'pdf_export'
            action_url = job.download_url
            action_text = "Télécharger"
        elif status == 'failed':
            title = "Erreur d'export PDF"
            message = f"L'export '{job.export_type}' a échoué: {job.error_message}"
            notification_type = 'pdf_export'
            action_url = None
            action_text = None
        else:
            return
        
        # Créer la notification
        Notification.objects.create(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            action_text=action_text,
            priority='medium'
        )
        
        logger.info(f"Notification envoyée à l'utilisateur {user_id} pour le job {job_id}")
        
    except (User.DoesNotExist, PDFExportJob.DoesNotExist):
        logger.error(f"Utilisateur ou job non trouvé: user_id={user_id}, job_id={job_id}")
    except Exception as exc:
        logger.error(f"Erreur lors de l'envoi de notification: {str(exc)}")


@shared_task
def generate_analytics_report():
    """
    Générer un rapport d'analytics sur l'utilisation des exports PDF
    Tâche à exécuter périodiquement
    """
    
    try:
        from django.db.models import Count, Avg, Sum
        from django.utils import timezone
        
        # Statistiques des 30 derniers jours
        start_date = timezone.now() - timedelta(days=30)
        
        jobs = PDFExportJob.objects.filter(created_at__gte=start_date)
        
        stats = {
            'total_jobs': jobs.count(),
            'successful_jobs': jobs.filter(status='completed').count(),
            'failed_jobs': jobs.filter(status='failed').count(),
            'average_processing_time': jobs.filter(
                status='completed',
                processing_time__isnull=False
            ).aggregate(Avg('processing_time'))['processing_time__avg'] or 0,
            'total_file_size': jobs.filter(
                status='completed'
            ).aggregate(Sum('file_size'))['file_size__sum'] or 0,
            'export_types': jobs.values('export_type').annotate(
                count=Count('export_type')
            ).order_by('-count'),
            'users_stats': jobs.values(
                'created_by__username'
            ).annotate(
                count=Count('job_id')
            ).order_by('-count')[:10]
        }
        
        # Calculer le taux de succès
        if stats['total_jobs'] > 0:
            stats['success_rate'] = (stats['successful_jobs'] / stats['total_jobs']) * 100
        else:
            stats['success_rate'] = 0
        
        logger.info(f"Rapport d'analytics généré: {stats}")
        
        return stats
        
    except Exception as exc:
        logger.error(f"Erreur génération rapport analytics: {str(exc)}")
        return None


# Fonctions utilitaires

def get_pdf_generator(export_type: str):
    """
    Retourner le générateur PDF approprié selon le type
    
    Args:
        export_type: Type d'export
    
    Returns:
        Instance du générateur PDF
    """
    
    return PDFGeneratorFactory.create_generator(export_type)


def format_file_size(size_bytes: int) -> str:
    """
    Formater la taille de fichier en format lisible
    
    Args:
        size_bytes: Taille en bytes
    
    Returns:
        Taille formatée (ex: "2.5 MB")
    """
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes = size_bytes / 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_bulk_zip(job_results: list, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Créer un fichier ZIP contenant plusieurs PDFs
    
    Args:
        job_results: Résultats des jobs individuels
        settings: Paramètres pour le ZIP
    
    Returns:
        Dict avec les informations du fichier ZIP
    """
    
    try:
        import zipfile
        
        # Créer un fichier ZIP temporaire
        zip_filename = f"bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for result in job_results:
                if result.get('success') and result.get('filename'):
                    # Ajouter le fichier au ZIP
                    file_path = result.get('file_path')
                    if file_path and os.path.exists(file_path):
                        zipf.write(file_path, result['filename'])
        
        # Retourner les informations du ZIP
        zip_size = os.path.getsize(zip_path)
        
        return {
            'success': True,
            'filename': zip_filename,
            'path': zip_path,
            'size': zip_size,
            'size_display': format_file_size(zip_size)
        }
        
    except Exception as exc:
        logger.error(f"Erreur création ZIP: {str(exc)}")
        return {
            'success': False,
            'error': str(exc)
        }


def create_simple_pdf(title: str, content: str) -> bytes:
    """
    Créer un PDF simple pour les tests
    
    Args:
        title: Titre du document
        content: Contenu du document
    
    Returns:
        Données PDF en bytes
    """
    
    if not REPORTLAB_AVAILABLE:
        # Créer un PDF simple sans ReportLab
        pdf_content = f"""
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
({title}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF
""".replace('{title}', title)
        return pdf_content.encode('latin-1')
    
    # Avec ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(content, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
