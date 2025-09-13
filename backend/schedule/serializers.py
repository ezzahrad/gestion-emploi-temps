from rest_framework import serializers
from .models import Schedule, Absence, MakeupSession

class ScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = '__all__'
        
    def validate(self, data):
        # Validate time range
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError('L\'heure de début doit être antérieure à l\'heure de fin.')
        
        return data

class AbsenceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Absence
        fields = '__all__'
        read_only_fields = ('created_by', 'approved_by')

class MakeupSessionSerializer(serializers.ModelSerializer):
    schedule_title = serializers.CharField(source='original_schedule.title', read_only=True)
    room_name = serializers.CharField(source='new_room.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = MakeupSession
        fields = '__all__'
        read_only_fields = ('requested_by', 'approved_by')