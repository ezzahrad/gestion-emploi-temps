from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AbsencePolicy, Absence, MakeupSession, 
    AttendanceRecord, StudentAbsenceStatistics
)
from schedule.models import Schedule
from core.models import Room

User = get_user_model()

class AbsencePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsencePolicy
        fields = '__all__'

class AbsenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    schedule_details = serializers.SerializerMethodField()
    reported_by_name = serializers.CharField(source='reported_by.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    is_justification_overdue = serializers.SerializerMethodField()
    can_request_makeup = serializers.SerializerMethodField()
    justification_document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Absence
        fields = [
            'id', 'student', 'student_name', 'schedule', 'schedule_details',
            'absence_type', 'reason', 'justification_document', 'justification_document_url',
            'status', 'is_makeup_required', 'makeup_completed', 'reported_by',
            'reported_by_name', 'approved_by', 'approved_by_name', 'absence_date',
            'reported_at', 'approved_at', 'justification_deadline', 'admin_comments',
            'is_justification_overdue', 'can_request_makeup', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'reported_by', 'approved_by', 'approved_at', 'justification_deadline',
            'created_at', 'updated_at'
        ]
    
    def get_schedule_details(self, obj):
        return obj.get_schedule_details()
    
    def get_is_justification_overdue(self, obj):
        return obj.is_justification_overdue()
    
    def get_can_request_makeup(self, obj):
        return obj.can_request_makeup()
    
    def get_justification_document_url(self, obj):
        if obj.justification_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.justification_document.url)
        return None

class StudentAbsenceSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les absences vues par l'étudiant (données limitées)"""
    schedule_details = serializers.SerializerMethodField()
    is_justification_overdue = serializers.SerializerMethodField()
    can_request_makeup = serializers.SerializerMethodField()
    justification_document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Absence
        fields = [
            'id', 'schedule_details', 'absence_type', 'reason',
            'justification_document_url', 'status', 'is_makeup_required',
            'makeup_completed', 'absence_date', 'reported_at',
            'justification_deadline', 'is_justification_overdue',
            'can_request_makeup'
        ]
    
    def get_schedule_details(self, obj):
        return obj.get_schedule_details()
    
    def get_is_justification_overdue(self, obj):
        return obj.is_justification_overdue()
    
    def get_can_request_makeup(self, obj):
        return obj.can_request_makeup()
    
    def get_justification_document_url(self, obj):
        if obj.justification_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.justification_document.url)
        return None

class MakeupSessionSerializer(serializers.ModelSerializer):
    absence_details = AbsenceSerializer(source='absence', read_only=True)
    student_name = serializers.CharField(source='absence.student.full_name', read_only=True)
    subject_name = serializers.CharField(source='absence.schedule.subject_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    scheduled_by_name = serializers.CharField(source='scheduled_by.full_name', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.full_name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = MakeupSession
        fields = [
            'id', 'absence', 'absence_details', 'student_name', 'subject_name',
            'makeup_date', 'makeup_start_time', 'makeup_end_time', 'duration_minutes',
            'room', 'room_name', 'teacher', 'teacher_name', 'status',
            'attendance_confirmed', 'session_notes', 'student_feedback',
            'teacher_feedback', 'makeup_grade', 'is_successful', 'scheduled_by',
            'scheduled_by_name', 'confirmed_by', 'confirmed_by_name', 'created_at',
            'updated_at', 'confirmed_at'
        ]
        read_only_fields = [
            'scheduled_by', 'confirmed_by', 'confirmed_at', 'created_at', 'updated_at'
        ]
    
    def get_duration_minutes(self, obj):
        return obj.get_duration_minutes()

class StudentMakeupSessionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les sessions de rattrapage vues par l'étudiant"""
    subject_name = serializers.CharField(source='absence.schedule.subject_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    original_absence_date = serializers.DateField(source='absence.absence_date', read_only=True)
    
    class Meta:
        model = MakeupSession
        fields = [
            'id', 'subject_name', 'original_absence_date', 'makeup_date',
            'makeup_start_time', 'makeup_end_time', 'duration_minutes',
            'room_name', 'teacher_name', 'status', 'attendance_confirmed',
            'session_notes', 'student_feedback', 'is_successful', 'created_at'
        ]
    
    def get_duration_minutes(self, obj):
        return obj.get_duration_minutes()

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    schedule_details = serializers.SerializerMethodField()
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.full_name', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'student', 'student_name', 'schedule', 'schedule_details',
            'status', 'arrival_time', 'departure_time', 'minutes_late',
            'minutes_early_departure', 'notes', 'recorded_by', 'recorded_by_name',
            'recorded_at', 'is_validated', 'validated_by', 'validated_by_name',
            'validated_at'
        ]
        read_only_fields = [
            'minutes_late', 'minutes_early_departure', 'recorded_by',
            'recorded_at', 'validated_by', 'validated_at'
        ]
    
    def get_schedule_details(self, obj):
        return {
            'subject_name': obj.schedule.subject_name,
            'teacher_name': obj.schedule.teacher_name,
            'room_name': obj.schedule.room_name,
            'date': obj.schedule.week_start.strftime('%d/%m/%Y'),
            'start_time': obj.schedule.start_time,
            'end_time': obj.schedule.end_time,
            'day_name': obj.schedule.day_name
        }

class StudentAbsenceStatisticsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_program = serializers.CharField(source='student.program.name', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = StudentAbsenceStatistics
        fields = [
            'id', 'student', 'student_name', 'student_program', 'total_absences',
            'justified_absences', 'unjustified_absences', 'pending_absences',
            'absence_rate', 'justified_rate', 'pending_makeups', 'completed_makeups',
            'failed_makeups', 'is_at_risk', 'risk_level', 'risk_level_display',
            'last_calculated', 'period_start', 'period_end'
        ]
        read_only_fields = [
            'total_absences', 'justified_absences', 'unjustified_absences',
            'pending_absences', 'absence_rate', 'justified_rate',
            'pending_makeups', 'completed_makeups', 'failed_makeups',
            'is_at_risk', 'risk_level', 'last_calculated'
        ]

class BulkAttendanceCreateSerializer(serializers.Serializer):
    """Sérialiseur pour l'enregistrement en masse de présences"""
    schedule = serializers.IntegerField()
    attendance_records = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_schedule(self, value):
        try:
            return Schedule.objects.get(id=value)
        except Schedule.DoesNotExist:
            raise serializers.ValidationError("Planning non trouvé")
    
    def validate_attendance_records(self, value):
        """Valider le format des enregistrements de présence"""
        for record_data in value:
            if 'student_id' not in record_data or 'status' not in record_data:
                raise serializers.ValidationError(
                    "Chaque enregistrement doit contenir 'student_id' et 'status'"
                )
            
            if record_data['status'] not in ['present', 'absent', 'late', 'excused', 'left_early']:
                raise serializers.ValidationError(
                    f"Statut invalide: {record_data['status']}"
                )
        
        return value
    
    def create(self, validated_data):
        schedule = validated_data['schedule']
        records_data = validated_data['attendance_records']
        user = self.context['request'].user
        
        records_to_create = []
        errors = []
        
        for record_data in records_data:
            try:
                student = User.objects.get(
                    id=record_data['student_id'],
                    role='student'
                )
                
                # Vérifier que l'enregistrement n'existe pas déjà
                if AttendanceRecord.objects.filter(student=student, schedule=schedule).exists():
                    errors.append(f"Présence déjà enregistrée pour {student.full_name}")
                    continue
                
                records_to_create.append(
                    AttendanceRecord(
                        student=student,
                        schedule=schedule,
                        status=record_data['status'],
                        arrival_time=record_data.get('arrival_time'),
                        departure_time=record_data.get('departure_time'),
                        notes=record_data.get('notes', ''),
                        recorded_by=user
                    )
                )
                
            except User.DoesNotExist:
                errors.append(f"Étudiant non trouvé: {record_data['student_id']}")
        
        if errors:
            raise serializers.ValidationError({'errors': errors})
        
        # Créer tous les enregistrements en une fois
        created_records = AttendanceRecord.objects.bulk_create(records_to_create)
        
        return {
            'created_count': len(created_records),
            'schedule': schedule.id,
            'records': AttendanceRecordSerializer(created_records, many=True).data
        }

class AbsenceReportSerializer(serializers.Serializer):
    """Sérialiseur pour la génération de rapports d'absence"""
    student_id = serializers.IntegerField(required=False)
    program_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    absence_types = serializers.ListField(
        child=serializers.ChoiceField(choices=Absence.ABSENCE_TYPE_CHOICES),
        required=False
    )
    include_statistics = serializers.BooleanField(default=True)
    include_makeups = serializers.BooleanField(default=True)
    format = serializers.ChoiceField(choices=['json', 'pdf', 'excel'], default='json')
    
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        
        return data
