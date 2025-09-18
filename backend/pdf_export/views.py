from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import datetime, timedelta
import os
import mimetypes

from .models import PDFTemplate, PDFExportJob, PDFExportSettings, PDFExportStatistics
from .serializers import (
    PDFTemplateSerializer, PDFExportJobSerializer, PDFExportRequestSerializer,
    PDFExportSettingsSerializer, PDFExportStatisticsSerializer,
    BulkPDFExportSerializer, PDFJobStatusSerializer
)
from core.permissions import IsTeacherOrAdmin, IsStudentOrTeacher
from .tasks import process_pdf_export  # Tâche Celery (à créer)

User = get_user_model()

class PDFTemplateViewSet(viewsets.ModelViewSet):
    queryset = PDFTemplate.objects.filter(is_active=True)
    serializer_class = PDFTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_default', 'page_format', 'orientation']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'template_type', 'created_at']
    ordering = ['template_type', 'name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_as_default(self, request, pk=None):
        """Définir comme template par défaut pour son type"""
        template = self.get_object()
        
        # Retirer le statut par défaut des autres templates du même type
        PDFTemplate.objects.filter(
            template_type=template.template_type,
            is_default=True
        ).update(is_default=False)
        
        # Définir ce template comme par défaut
        template.is_default = True
        template.save()
        
        return Response({
            'message': f'Template "{template.name}" défini comme par défaut pour {template.get_template_type_display()}'
        })
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Obtenir les templates par type"""
        template_type = request.query_params.get('type')
        if not template_type:
            return Response(
                {'error': 'Paramètre type requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        templates = self.get_queryset().filter(template_type=template_type)
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

class PDFExportJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PDFExportJob.objects.all()
    serializer_class = PDFExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['export_type', 'status', 'template']
    search_fields = ['export_type', 'success_message', 'error_message']
    ordering_fields = ['created_at', 'completed_at', 'progress']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = PDFExportJob.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres exports
            queryset = queryset.filter(requested_by=user)
        elif user.role == 'teacher':
            # Les enseignants voient leurs exports et ceux liés à leurs cours
            queryset = queryset.filter(
                models.Q(requested_by=user) |
                models.Q(export_parameters__teacher_id=user.id)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger le fichier PDF généré"""
        job = self.get_object()
        
        # Vérifier que le job est terminé
        if job.status != 'completed':
            return Response(
                {'error': 'Export non terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le fichier existe
        if not job.file_path or not os.path.exists(job.file_path):
            return Response(
                {'error': 'Fichier non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que le fichier n'a pas expiré
        if job.expires_at and timezone.now() > job.expires_at:
            return Response(
                {'error': 'Fichier expiré'},
                status=status.HTTP_410_GONE
            )
        
        # Enregistrer le téléchargement
        from .models import PDFDownloadLog
        PDFDownloadLog.objects.create(
            export_job=job,
            downloaded_by=request.user,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            bytes_transferred=job.file_size
        )
        
        # Retourner le fichier
        response = FileResponse(
            open(job.file_path, 'rb'),
            content_type='application/pdf'
        )
        filename = f"{job.get_export_type_display()}_{job.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un export en cours"""
        job = self.get_object()
        
        if job.status not in ['pending', 'processing']:
            return Response(
                {'error': 'Impossible d\'annuler cet export'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'cancelled'
        job.completed_at = timezone.now()
        job.save()
        
        return Response({'message': 'Export annulé avec succès'})
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Obtenir les jobs de l'utilisateur connecté"""
        jobs = self.get_queryset().filter(requested_by=request.user)
        serializer = PDFJobStatusSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Obtenir le statut d'un job par son UUID"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = PDFExportJob.objects.get(job_id=job_id)
            # Vérifier les permissions
            if (request.user.role == 'student' and job.requested_by != request.user):
                return Response(
                    {'error': 'Accès non autorisé'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = PDFJobStatusSerializer(job)
            return Response(serializer.data)
            
        except PDFExportJob.DoesNotExist:
            return Response(
                {'error': 'Job non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

class PDFExportViewSet(viewsets.GenericViewSet):
    """ViewSet pour créer des exports PDF"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_export(self, request):
        """Créer une nouvelle demande d'export PDF"""
        serializer = PDFExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier les limites de l'utilisateur
        settings_obj = PDFExportSettings.objects.first()
        if settings_obj:
            # Vérifier le nombre de jobs en cours
            concurrent_jobs = PDFExportJob.objects.filter(
                requested_by=request.user,
                status__in=['pending', 'processing']
            ).count()
            
            if concurrent_jobs >= settings_obj.max_concurrent_jobs:
                return Response(
                    {'error': f'Limite de {settings_obj.max_concurrent_jobs} exports simultanés atteinte'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        
        # Créer le job
        job_data = serializer.validated_data
        export_type = job_data.pop('export_type')
        template_id = job_data.pop('template_id', None)
        
        template = None
        if template_id:
            try:
                template = PDFTemplate.objects.get(id=template_id)
            except PDFTemplate.DoesNotExist:
                # Utiliser le template par défaut
                template = PDFTemplate.objects.filter(
                    template_type=export_type,
                    is_default=True
                ).first()
        
        job = PDFExportJob.objects.create(
            export_type=export_type,
            template=template,
            export_parameters=job_data,
            requested_by=request.user
        )
        
        # Lancer la tâche asynchrone
        try:
            # En production, utiliser Celery
            # process_pdf_export.delay(job.id)
            
            # En développement, traitement synchrone (à adapter)
            from .pdf_service import PDFExportService
            service = PDFExportService()
            service.process_export(job.id)
            
        except Exception as e:
            job.mark_as_failed(str(e))
            return Response(
                {'error': 'Erreur lors du lancement de l\'export'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'job_id': str(job.job_id),
            'message': 'Export lancé avec succès',
            'status_url': f'/api/pdf-export/jobs/status/?job_id={job.job_id}'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def bulk_export(self, request):
        """Créer un export en masse"""
        serializer = BulkPDFExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer le job d'export en masse
        job_data = serializer.validated_data
        export_type = job_data.pop('export_type')
        template_id = job_data.pop('template_id', None)
        
        template = None
        if template_id:
            try:
                template = PDFTemplate.objects.get(id=template_id)
            except PDFTemplate.DoesNotExist:
                pass
        
        job = PDFExportJob.objects.create(
            export_type=export_type,
            template=template,
            export_parameters=job_data,
            requested_by=request.user
        )
        
        # Lancer la tâche asynchrone
        try:
            from .pdf_service import PDFExportService
            service = PDFExportService()
            service.process_bulk_export(job.id)
            
        except Exception as e:
            job.mark_as_failed(str(e))
            return Response(
                {'error': 'Erreur lors du lancement de l\'export en masse'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'job_id': str(job.job_id),
            'message': 'Export en masse lancé avec succès',
            'status_url': f'/api/pdf-export/jobs/status/?job_id={job.job_id}'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def available_types(self, request):
        """Obtenir les types d'export disponibles pour l'utilisateur"""
        user = request.user
        
        types = []
        
        if user.role == 'student':
            types = [
                {'value': 'schedule', 'label': 'Mon emploi du temps'},
                {'value': 'transcript', 'label': 'Mon relevé de notes'},
                {'value': 'absence_report', 'label': 'Mon rapport d\'absences'}
            ]
        
        elif user.role == 'teacher':
            types = [
                {'value': 'teacher_schedule', 'label': 'Mon planning enseignant'},
                {'value': 'bulk_schedules', 'label': 'Emplois du temps étudiants'},
                {'value': 'attendance_report', 'label': 'Rapport de présences'},
                {'value': 'absence_report', 'label': 'Rapport d\'absences'}
            ]
        
        elif user.role in ['admin', 'department_head', 'program_head']:
            types = [
                {'value': 'schedule', 'label': 'Emploi du temps étudiant'},
                {'value': 'teacher_schedule', 'label': 'Planning enseignant'},
                {'value': 'room_schedule', 'label': 'Planning salle'},
                {'value': 'transcript', 'label': 'Relevé de notes'},
                {'value': 'bulk_schedules', 'label': 'Emplois du temps en masse'},
                {'value': 'bulk_transcripts', 'label': 'Relevés de notes en masse'},
                {'value': 'absence_report', 'label': 'Rapport d\'absences'},
                {'value': 'attendance_report', 'label': 'Rapport de présences'}
            ]
        
        return Response(types)

class PDFExportSettingsViewSet(viewsets.ModelViewSet):
    queryset = PDFExportSettings.objects.all()
    serializer_class = PDFExportSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    
    def get_queryset(self):
        # Il ne devrait y avoir qu'une seule instance de configuration
        return PDFExportSettings.objects.all()[:1]

class PDFExportStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PDFExportStatistics.objects.all()
    serializer_class = PDFExportStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_exports']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des statistiques"""
        # Derniers 30 jours
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_stats = self.get_queryset().filter(date__gte=thirty_days_ago)
        
        if not recent_stats.exists():
            return Response({
                'period': '30 derniers jours',
                'total_exports': 0,
                'success_rate': 0,
                'average_file_size_mb': 0,
                'total_pages': 0
            })
        
        # Calculer les totaux
        total_exports = sum(stat.total_exports for stat in recent_stats)
        successful_exports = sum(stat.successful_exports for stat in recent_stats)
        total_file_size = sum(stat.total_file_size_mb for stat in recent_stats)
        total_pages = sum(stat.total_pages_generated for stat in recent_stats)
        
        summary = {
            'period': '30 derniers jours',
            'total_exports': total_exports,
            'successful_exports': successful_exports,
            'failed_exports': total_exports - successful_exports,
            'success_rate': (successful_exports / total_exports * 100) if total_exports > 0 else 0,
            'total_file_size_mb': total_file_size,
            'average_file_size_mb': (total_file_size / successful_exports) if successful_exports > 0 else 0,
            'total_pages': total_pages,
            'daily_average': total_exports / 30,
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Tendances des exports"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        stats = self.get_queryset().filter(date__gte=start_date).order_by('date')
        
        trends = []
        for stat in stats:
            trends.append({
                'date': stat.date.isoformat(),
                'total_exports': stat.total_exports,
                'successful_exports': stat.successful_exports,
                'failed_exports': stat.failed_exports,
                'success_rate': (stat.successful_exports / stat.total_exports * 100) if stat.total_exports > 0 else 0
            })
        
        return Response({
            'period_days': days,
            'trends': trends
        })
