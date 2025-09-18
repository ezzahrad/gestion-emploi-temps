from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PDFTemplate, PDFExportJob, PDFExportSettings, PDFExportStatistics

User = get_user_model()

class PDFTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = PDFTemplate
        fields = [
            'id', 'name', 'template_type', 'description', 'page_format',
            'orientation', 'margin_top', 'margin_bottom', 'margin_left',
            'margin_right', 'header_template', 'footer_template', 'css_styles',
            'is_default', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class PDFExportJobSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    download_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFExportJob
        fields = [
            'job_id', 'export_type', 'template', 'template_name', 'status',
            'progress', 'export_parameters', 'file_path', 'file_size',
            'file_size_display', 'page_count', 'success_message', 'error_message',
            'error_details', 'requested_by', 'requested_by_name', 'download_url',
            'processing_time', 'created_at', 'started_at', 'completed_at', 'expires_at'
        ]
        read_only_fields = [
            'job_id', 'status', 'progress', 'file_path', 'file_size',
            'page_count', 'success_message', 'error_message', 'error_details',
            'requested_by', 'created_at', 'started_at', 'completed_at', 'expires_at'
        ]
    
    def get_download_url(self, obj):
        return obj.get_download_url()
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()
    
    def get_processing_time(self, obj):
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return duration.total_seconds()
        return None

class PDFExportRequestSerializer(serializers.Serializer):
    """Sérialiseur pour les demandes d'export PDF"""
    export_type = serializers.ChoiceField(choices=PDFExportJob.EXPORT_TYPE_CHOICES)
    template_id = serializers.IntegerField(required=False)
    
    # Paramètres communs
    format = serializers.ChoiceField(choices=['A4', 'A3', 'Letter'], default='A4')
    orientation = serializers.ChoiceField(choices=['portrait', 'landscape'], default='portrait')
    include_details = serializers.BooleanField(default=True)
    include_statistics = serializers.BooleanField(default=False)
    watermark = serializers.CharField(required=False, max_length=200)
    
    # Paramètres spécifiques selon le type
    student_id = serializers.IntegerField(required=False)
    program_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)
    teacher_id = serializers.IntegerField(required=False)
    room_id = serializers.IntegerField(required=False)
    
    # Période
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    academic_year = serializers.CharField(required=False, max_length=9)
    semester = serializers.IntegerField(required=False)
    
    # Options de filtrage
    absence_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    grade_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate(self, data):
        export_type = data['export_type']
        
        # Validation selon le type d'export
        if export_type in ['schedule', 'transcript', 'absence_report']:
            if not data.get('student_id'):
                raise serializers.ValidationError(
                    f"student_id requis pour le type {export_type}"
                )
        
        if export_type in ['teacher_schedule']:
            if not data.get('teacher_id'):
                raise serializers.ValidationError(
                    "teacher_id requis pour les plannings enseignant"
                )
        
        if export_type in ['room_schedule']:
            if not data.get('room_id'):
                raise serializers.ValidationError(
                    "room_id requis pour les plannings salle"
                )
        
        # Validation des dates
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "start_date doit être antérieure à end_date"
            )
        
        return data

class PDFExportSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFExportSettings
        fields = '__all__'

class PDFExportStatisticsSerializer(serializers.ModelSerializer):
    success_rate = serializers.SerializerMethodField()
    average_file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFExportStatistics
        fields = [
            'date', 'total_exports', 'successful_exports', 'failed_exports',
            'success_rate', 'schedule_exports', 'transcript_exports', 
            'report_exports', 'total_file_size_mb', 'average_file_size_mb',
            'total_pages_generated', 'average_processing_time_seconds',
            'peak_concurrent_jobs'
        ]
    
    def get_success_rate(self, obj):
        if obj.total_exports > 0:
            return (obj.successful_exports / obj.total_exports) * 100
        return 0
    
    def get_average_file_size_mb(self, obj):
        if obj.successful_exports > 0:
            return obj.total_file_size_mb / obj.successful_exports
        return 0

class BulkPDFExportSerializer(serializers.Serializer):
    """Sérialiseur pour l'export en masse"""
    export_type = serializers.ChoiceField(choices=['bulk_schedules', 'bulk_transcripts'])
    template_id = serializers.IntegerField(required=False)
    
    # Critères de sélection
    program_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    # Options
    format = serializers.ChoiceField(choices=['A4', 'A3', 'Letter'], default='A4')
    orientation = serializers.ChoiceField(choices=['portrait', 'landscape'], default='portrait')
    combine_in_single_file = serializers.BooleanField(default=False)
    include_cover_page = serializers.BooleanField(default=True)
    
    # Période pour les emplois du temps
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        # Au moins un critère de sélection doit être fourni
        if not any([
            data.get('program_ids'),
            data.get('department_ids'),
            data.get('student_ids')
        ]):
            raise serializers.ValidationError(
                "Au moins un critère de sélection doit être fourni"
            )
        
        # Validation des dates pour les emplois du temps
        if data['export_type'] == 'bulk_schedules':
            if not data.get('start_date') or not data.get('end_date'):
                raise serializers.ValidationError(
                    "start_date et end_date sont requis pour les emplois du temps"
                )
        
        return data

class PDFJobStatusSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour le statut des jobs"""
    download_url = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PDFExportJob
        fields = [
            'job_id', 'export_type', 'status', 'progress', 'download_url',
            'file_size_display', 'page_count', 'error_message', 'created_at',
            'completed_at', 'expires_at'
        ]
    
    def get_download_url(self, obj):
        return obj.get_download_url()
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()
