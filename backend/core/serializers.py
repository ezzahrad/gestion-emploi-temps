from rest_framework import serializers
from .models import Department, Program, Room, Subject, Teacher, Student, TeacherAvailability
from authentication.serializers import UserSerializer

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.full_name', read_only=True)
    programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
    
    def get_programs_count(self, obj):
        return obj.programs.count()

class ProgramSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    head_name = serializers.CharField(source='head.full_name', read_only=True)
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = '__all__'
        
    def get_students_count(self, obj):
        return obj.students.count()

class RoomSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    teachers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = '__all__'
        
    def get_teachers_count(self, obj):
        return obj.teachers.count()

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    subjects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = '__all__'
        
    def get_subjects_count(self, obj):
        return obj.subjects.count()

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'

class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TeacherAvailability
        fields = '__all__'