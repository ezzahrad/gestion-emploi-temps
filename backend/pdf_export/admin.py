from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import (
    PDFTemplate, PDFExportJob, PDFExportSettings, 
    PDFExportStatistics, PDFDownloadLog
)

@admin.register(PDFTemplate)
class PDFTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type_display', 'page_format', 'orientation', 
        'is_default', 'is_active', 'created_by_name', 'created_at'
    ]
    list_filter = ['template_type', 'page_format', 'orientation', 'is_default', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'template_type', 'description', 'is_default', 'is_active')
        }),
        ('Configuration de page', {
            'fields': (
                ('page_format', 'orientation'),
                ('margin_top', 'margin_bottom'),
                ('margin_left', 'margin_right')
            )
        }),
        ('Templates HTML', {
            'fields': ('header_template', 'footer_template'),
            'classes': ('collapse',)
        }),
        ('Styles CSS', {
            'fields': ('css_styles',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_by']
    
    actions = ['activate_templates', 'deactivate_templates', 'set_as_default']
    
    def template_type_display(self, obj):
        return obj.get_template_type_display()
    template_type_display.short_description = 'Type'
    
    def created_by_name(self, obj):
        return obj.created_by.full_name
    created_by_name.short_description = 'Créé par'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def activate_templates(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} templates activés.')
    activate_templates.short_description = 'Activer les templates sélectionnés'
    
    def deactivate_templates(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} templates désactivés.')
    deactivate_templates.short_description = 'Désactiver les templates sélectionnés'
    
    def set_as_default(self, request, queryset):
        count = 0
        for template in queryset:
            # Retirer le statut par défaut des autres templates du même type
            PDFTemplate.objects.filter(
                template_type=template.template_type,
                is_default=True
            ).update(is_default=False)
            
            # Définir ce template comme par défaut
            template.is_default = True
            template.save()
            count += 1
        
        self.message_user(request, f'{count} templates définis comme par défaut.')
    set_as_default.short_description = 'Définir comme template par défaut'

@admin.register(PDFExportJob)
class PDFExportJobAdmin(admin.ModelAdmin):
    list_display = [
        'job_id_short', 'export_type_display', 'requested_by_name', 
        'status_display', 'progress_display', 'file_size_display', 
        'created_at', 'processing_time'
    ]
    list_filter = ['export_type', 'status', 'created_at', 'completed_at']
    search_fields = ['job_id', 'requested_by__first_name', 'requested_by__last_name', 'error_message']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('job_id', 'export_type', 'template', 'requested_by')
        }),
        ('Statut et progression', {
            'fields': ('status', 'progress', 'started_at', 'completed_at')
        }),
        ('Paramètres d\'export', {
            'fields': ('export_parameters',),
            'classes': ('collapse',)
        }),
        ('Résultats', {
            'fields': ('file_path', 'file_size', 'page_count', 'success_message')
        }),
        ('Erreurs', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('expires_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'job_id', 'status', 'progress', 'file_path', 'file_size', 
        'page_count', 'success_message', 'error_message', 'error_details',
        'started_at', 'completed_at', 'expires_at'
    ]
    
    actions = ['cancel_jobs', 'cleanup_expired_jobs']
    
    def job_id_short(self, obj):
        return str(obj.job_id)[:8] + '...'
    job_id_short.short_description = 'Job ID'
    
    def export_type_display(self, obj):
        return obj.get_export_type_display()
    export_type_display.short_description = 'Type d\'export'
    
    def requested_by_name(self, obj):
        return obj.requested_by.full_name
    requested_by_name.short_description = 'Demandé par'
    
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'
    
    def progress_display(self, obj):
        if obj.status == 'completed':
            return format_html('<span style="color: green;">100%</span>')
        elif obj.status == 'failed':
            return format_html('<span style="color: red;">Échec</span>')
        elif obj.status == 'cancelled':
            return format_html('<span style="color: gray;">Annulé</span>')
        else:
            return f"{obj.progress}%"
    progress_display.short_description = 'Progression'
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'Taille fichier'
    
    def processing_time(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return f"{duration.total_seconds():.1f}s"
        return "-"
    processing_time.short_description = 'Temps de traitement'
    
    def cancel_jobs(self, request, queryset):
        count = 0
        for job in queryset.filter(status__in=['pending', 'processing']):
            job.status = 'cancelled'
            job.completed_at = timezone.now()
            job.save()
            count += 1
        
        self.message_user(request, f'{count} jobs annulés.')
    cancel_jobs.short_description = 'Annuler les jobs sélectionnés'
    
    def cleanup_expired_jobs(self, request, queryset):
        count = 0
        for job in queryset.filter(
            expires_at__lt=timezone.now(),
            status='completed'
        ):
            # Supprimer le fichier
            if job.file_path and os.path.exists(job.file_path):
                try:
                    os.remove(job.file_path)
                except OSError:
                    pass
            
            job.delete()
            count += 1
        
        self.message_user(request, f'{count} jobs expirés supprimés.')
    cleanup_expired_jobs.short_description = 'Nettoyer les jobs expirés'

@admin.register(PDFExportSettings)
class PDFExportSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'max_file_size_mb', 'max_concurrent_jobs', 'job_retention_days', 'updated_at']
    
    fieldsets = (
        ('Répertoires', {
            'fields': ('output_directory', 'temp_directory')
        }),
        ('Limites', {
            'fields': (
                'max_file_size_mb', 'max_pages_per_document', 
                'max_concurrent_jobs', 'job_retention_days'
            )
        }),
        ('Qualité et performance', {
            'fields': (
                'image_quality', 'compression_level', 'enable_parallelization'
            )
        }),
        ('Filigrane', {
            'fields': ('enable_watermark', 'watermark_text', 'watermark_opacity'),
            'classes': ('collapse',)
        }),
        ('Notifications email', {
            'fields': ('send_completion_email', 'admin_notification_email'),
            'classes': ('collapse',)
        }),
        ('Sécurité', {
            'fields': ('require_authentication', 'allow_public_downloads'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Il ne devrait y avoir qu'une seule instance de configuration
        return not PDFExportSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PDFExportStatistics)
class PDFExportStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_exports', 'success_rate_display', 'schedule_exports',
        'transcript_exports', 'report_exports', 'total_file_size_mb',
        'average_processing_time_seconds'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    
    readonly_fields = [
        'total_exports', 'successful_exports', 'failed_exports',
        'schedule_exports', 'transcript_exports', 'report_exports',
        'total_file_size_mb', 'total_pages_generated',
        'average_processing_time_seconds', 'peak_concurrent_jobs'
    ]
    
    def success_rate_display(self, obj):
        if obj.total_exports > 0:
            rate = (obj.successful_exports / obj.total_exports) * 100
            color = 'green' if rate >= 95 else 'orange' if rate >= 80 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return '0%'
    success_rate_display.short_description = 'Taux de succès'
    
    def has_add_permission(self, request):
        return False  # Les statistiques sont générées automatiquement
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PDFDownloadLog)
class PDFDownloadLogAdmin(admin.ModelAdmin):
    list_display = [
        'export_job_type', 'downloaded_by_name', 'download_successful',
        'bytes_transferred_display', 'ip_address', 'created_at'
    ]
    list_filter = ['download_successful', 'created_at', 'export_job__export_type']
    search_fields = [
        'downloaded_by__first_name', 'downloaded_by__last_name',
        'ip_address', 'user_agent'
    ]
    date_hierarchy = 'created_at'
    
    readonly_fields = [
        'export_job', 'downloaded_by', 'ip_address', 'user_agent',
        'download_successful', 'bytes_transferred', 'created_at'
    ]
    
    def export_job_type(self, obj):
        return obj.export_job.get_export_type_display()
    export_job_type.short_description = 'Type d\'export'
    
    def downloaded_by_name(self, obj):
        return obj.downloaded_by.full_name
    downloaded_by_name.short_description = 'Téléchargé par'
    
    def bytes_transferred_display(self, obj):
        if obj.bytes_transferred:
            if obj.bytes_transferred < 1024:
                return f"{obj.bytes_transferred} B"
            elif obj.bytes_transferred < 1024 * 1024:
                return f"{obj.bytes_transferred / 1024:.1f} KB"
            else:
                return f"{obj.bytes_transferred / (1024 * 1024):.1f} MB"
        return "N/A"
    bytes_transferred_display.short_description = 'Taille transférée'
    
    def has_add_permission(self, request):
        return False  # Les logs sont créés automatiquement
    
    def has_change_permission(self, request, obj=None):
        return False
