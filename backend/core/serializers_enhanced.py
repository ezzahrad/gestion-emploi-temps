# serializers.py - Sérialiseurs améliorés pour AppGET
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Department, Program, Room, Subject, Teacher, Student,
    TimeSlot, Schedule, ExcelImportLog, TimetableGeneration
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Sérialiseur basique pour les utilisateurs"""
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role']


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    total_programs = serializers.SerializerMethodField()
    total_teachers = serializers.SerializerMethodField()
    total_rooms = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
    
    def get_total_programs(self, obj):
        return obj.programs.filter(is_active=True).count()
    
    def get_total_teachers(self, obj):
        return obj.teachers.filter(is_available=True).count()
    
    def get_total_rooms(self, obj):
        return obj.rooms.filter(is_available=True).count()


class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    total_students = serializers.SerializerMethodField()
    total_subjects = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Program
        fields = '__all__'
    
    def get_total_students(self, obj):
        return obj.students.filter(is_active=True).count()
    
    def get_total_subjects(self, obj):
        return obj.subjects.filter(is_active=True).count()


class RoomSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    equipment_list = serializers.ReadOnlyField()
    current_usage = serializers.SerializerMethodField()
    availability_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = '__all__'
    
    def get_current_usage(self, obj):
        """Pourcentage d'utilisation actuel de la salle"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        total_schedules = obj.schedules.filter(
            start_date__lte=week_end,
            end_date__gte=week_start,
            is_active=True,
            is_cancelled=False
        ).count()
        
        # Supposons 40 créneaux possibles par semaine
        max_possible = 40
        return round((total_schedules / max_possible) * 100, 2) if max_possible > 0 else 0
    
    def get_availability_score(self, obj):
        """Score de disponibilité (0-10)"""
        if not obj.is_available:
            return 0
        
        usage = self.get_current_usage(obj)
        score = 10 - (usage / 10)  # Plus l'usage est élevé, plus le score diminue
        return max(0, min(10, round(score, 1)))


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_type_display = serializers.CharField(source='get_subject_type_display', read_only=True)
    programs_list = serializers.StringRelatedField(source='programs', many=True, read_only=True)
    teachers_list = serializers.StringRelatedField(source='teachers', many=True, read_only=True)
    required_equipment_list = serializers.ReadOnlyField()
    total_scheduled_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = '__all__'
    
    def get_total_scheduled_hours(self, obj):
        """Total des heures déjà planifiées pour cette matière"""
        scheduled_sessions = obj.schedules.filter(is_active=True, is_cancelled=False)
        total_minutes = sum([session.duration_minutes for session in scheduled_sessions])
        return round(total_minutes / 60, 2)


class TeacherSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    teacher_type_display = serializers.CharField(source='get_teacher_type_display', read_only=True)
    subjects_list = serializers.StringRelatedField(source='subjects', many=True, read_only=True)
    departments_list = serializers.StringRelatedField(source='departments', many=True, read_only=True)
    preferred_slots = serializers.ReadOnlyField()
    unavailable_slots_list = serializers.ReadOnlyField()
    current_workload = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = '__all__'
    
    def get_current_workload(self, obj):
        """Charge de travail actuelle en heures par semaine"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        scheduled_sessions = obj.schedules.filter(
            start_date__lte=week_end,
            end_date__gte=week_start,
            is_active=True,
            is_cancelled=False
        )
        
        total_minutes = sum([session.duration_minutes for session in scheduled_sessions])
        return round(total_minutes / 60, 2)
    
    def get_availability_status(self, obj):
        """État de disponibilité"""
        if not obj.is_available:
            return 'indisponible'
        
        workload = self.get_current_workload(obj)
        if workload >= obj.max_hours_per_week:
            return 'surchargé'
        elif workload >= obj.max_hours_per_week * 0.8:
            return 'occupé'
        elif workload >= obj.max_hours_per_week * 0.5:
            return 'modéré'
        else:
            return 'disponible'


class StudentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)
    current_schedules_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
    
    def get_current_schedules_count(self, obj):
        """Nombre de cours actuels de l'étudiant"""
        from django.utils import timezone
        
        today = timezone.now().date()
        return obj.program.schedules.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True,
            is_cancelled=False
        ).count()


class TimeSlotSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    current_usage = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = '__all__'
    
    def get_current_usage(self, obj):
        """Nombre de séances utilisant ce créneau cette semaine"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        return obj.schedules.filter(
            start_date__lte=week_end,
            end_date__gte=week_start,
            is_active=True,
            is_cancelled=False
        ).count()


class ScheduleListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des emplois du temps"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_capacity = serializers.IntegerField(source='room.capacity', read_only=True)
    time_slot_info = TimeSlotSerializer(source='time_slot', read_only=True)
    programs_list = serializers.StringRelatedField(source='programs', many=True, read_only=True)
    student_count = serializers.ReadOnlyField()
    is_room_suitable = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'title', 'subject_name', 'subject_code', 'teacher_name',
            'room_name', 'room_capacity', 'time_slot_info', 'programs_list',
            'start_date', 'end_date', 'session_number', 'total_sessions',
            'duration_minutes', 'student_count', 'is_room_suitable',
            'is_active', 'is_cancelled', 'is_makeup', 'notes'
        ]


class ScheduleDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur détaillé pour un emploi du temps"""
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    programs = ProgramSerializer(many=True, read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    student_count = serializers.ReadOnlyField()
    is_room_suitable = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer/modifier un emploi du temps"""
    
    class Meta:
        model = Schedule
        fields = [
            'title', 'subject', 'teacher', 'room', 'programs', 'time_slot',
            'start_date', 'end_date', 'session_number', 'total_sessions',
            'duration_minutes', 'notes', 'required_students'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier que la date de fin >= date de début
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("La date de fin doit être postérieure à la date de début.")
        
        # Vérifier la capacité de la salle vs nombre d'étudiants
        room = data['room']
        programs = data.get('programs', [])
        total_students = sum([program.students.filter(is_active=True).count() for program in programs])
        
        if total_students > room.capacity:
            raise serializers.ValidationError(
                f"La salle {room.name} (capacité: {room.capacity}) est trop petite pour "
                f"{total_students} étudiants."
            )
        
        return data


class ExcelImportLogSerializer(serializers.ModelSerializer):
    imported_by_name = serializers.CharField(source='imported_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ExcelImportLog
        fields = '__all__'
    
    def get_success_rate(self, obj):
        """Taux de succès de l'importation"""
        if obj.total_rows == 0:
            return 0
        return round((obj.successful_rows / obj.total_rows) * 100, 2)


class TimetableGenerationSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    programs_list = serializers.StringRelatedField(source='programs', many=True, read_only=True)
    efficiency_score = serializers.SerializerMethodField()
    
    class Meta:
        model = TimetableGeneration
        fields = '__all__'
    
    def get_efficiency_score(self, obj):
        """Score d'efficacité basé sur le temps de traitement et les conflits résolus"""
        if not obj.processing_time or obj.processing_time == 0:
            return 0
        
        # Score basé sur le nombre de sessions planifiées par minute de traitement
        sessions_per_minute = obj.total_sessions_planned / (obj.processing_time / 60)
        
        # Bonus pour les conflits résolus
        conflict_bonus = obj.conflicts_resolved * 0.1
        
        base_score = min(100, sessions_per_minute * 10 + conflict_bonus)
        return round(base_score, 2)


# Sérialiseurs pour les vues filtrées par rôle

class StudentScheduleViewSerializer(serializers.ModelSerializer):
    """Vue emploi du temps pour les étudiants"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    time_slot_info = TimeSlotSerializer(source='time_slot', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'title', 'subject_name', 'subject_code', 'teacher_name',
            'room_name', 'time_slot_info', 'start_date', 'end_date',
            'duration_minutes', 'notes', 'is_cancelled', 'is_makeup'
        ]


class TeacherScheduleViewSerializer(serializers.ModelSerializer):
    """Vue emploi du temps pour les enseignants"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_capacity = serializers.IntegerField(source='room.capacity', read_only=True)
    time_slot_info = TimeSlotSerializer(source='time_slot', read_only=True)
    programs_list = serializers.StringRelatedField(source='programs', many=True, read_only=True)
    student_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'title', 'subject_name', 'subject_code', 'room_name',
            'room_capacity', 'time_slot_info', 'programs_list',
            'start_date', 'end_date', 'session_number', 'total_sessions',
            'duration_minutes', 'student_count', 'notes', 'is_cancelled', 'is_makeup'
        ]


class RoomScheduleViewSerializer(serializers.ModelSerializer):
    """Vue emploi du temps pour les salles"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    programs_list = serializers.StringRelatedField(source='programs', many=True, read_only=True)
    time_slot_info = TimeSlotSerializer(source='time_slot', read_only=True)
    student_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'title', 'subject_name', 'teacher_name', 'programs_list',
            'time_slot_info', 'start_date', 'end_date', 'duration_minutes',
            'student_count', 'notes', 'is_cancelled'
        ]


# Sérialiseurs pour les statistiques et tableaux de bord

class DashboardStatsSerializer(serializers.Serializer):
    """Statistiques pour le tableau de bord"""
    total_departments = serializers.IntegerField()
    total_programs = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    total_subjects = serializers.IntegerField()
    total_schedules = serializers.IntegerField()
    active_schedules_this_week = serializers.IntegerField()
    room_utilization_rate = serializers.FloatField()
    teacher_workload_average = serializers.FloatField()


class WeeklyScheduleSerializer(serializers.Serializer):
    """Planning hebdomadaire"""
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    days = serializers.ListField(child=serializers.DictField())
    total_sessions = serializers.IntegerField()
    total_hours = serializers.FloatField()
