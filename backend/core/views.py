from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Department, Program, Room, Subject, Teacher, Student, TeacherAvailability
from schedule.models import Schedule
from .serializers import (
    DepartmentSerializer, ProgramSerializer, RoomSerializer, SubjectSerializer,
    TeacherSerializer, StudentSerializer, TeacherAvailabilitySerializer
)
from .permissions import IsAdminOrDepartmentHead, IsAdminOrProgramHead

# Department Views
class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code']
    search_fields = ['name', 'code']

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrDepartmentHead]

# Program Views
class ProgramListCreateView(generics.ListCreateAPIView):
    serializer_class = ProgramSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'level']
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Program.objects.all().order_by('name')
        elif user.role in ['department_head', 'program_head']:
            return Program.objects.filter(department=user.department).order_by('name')
        return Program.objects.none()

class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrProgramHead]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Program.objects.all().order_by('name')
        elif user.role in ['department_head', 'program_head']:
            return Program.objects.filter(department=user.department).order_by('name')
        return Program.objects.none()

# Room Views
class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'room_type', 'is_available']
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Room.objects.all().order_by('name')
        elif user.role in ['department_head', 'program_head']:
            return Room.objects.filter(department=user.department).order_by('name')
        return Room.objects.filter(department=user.department).order_by('name')

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Room.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Room.objects.filter(department=user.department)
        return Room.objects.filter(department=user.department)

# Subject Views
class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['department', 'subject_type', 'semester']
    search_fields = ['name', 'code']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Subject.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Subject.objects.filter(department=user.department)
        elif user.role == 'teacher':
            return Subject.objects.filter(teachers__user=user)
        return Subject.objects.none()

class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Subject.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Subject.objects.filter(department=user.department)
        elif user.role == 'teacher':
            return Subject.objects.filter(teachers__user=user)
        return Subject.objects.none()

# Teacher Views
class TeacherListCreateView(generics.ListCreateAPIView):
    serializer_class = TeacherSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_available']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Teacher.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Teacher.objects.filter(user__department=user.department)
        return Teacher.objects.none()

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeacherSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Teacher.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Teacher.objects.filter(user__department=user.department)
        elif user.role == 'teacher':
            return Teacher.objects.filter(user=user)
        return Teacher.objects.none()

# Student Views
class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program', 'enrollment_year', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'student_id']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Student.objects.filter(program__department=user.department)
        return Student.objects.none()

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Student.objects.filter(program__department=user.department)
        elif user.role == 'student':
            return Student.objects.filter(user=user)
        return Student.objects.none()

# Teacher Availability Views
class TeacherAvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = TeacherAvailabilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['teacher', 'day_of_week', 'is_available']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return TeacherAvailability.objects.filter(teacher__user=user)
        elif user.role in ['admin', 'department_head', 'program_head']:
            return TeacherAvailability.objects.all()
        return TeacherAvailability.objects.none()

class TeacherAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeacherAvailabilitySerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return TeacherAvailability.objects.filter(teacher__user=user)
        elif user.role in ['admin', 'department_head', 'program_head']:
            return TeacherAvailability.objects.all()
        return TeacherAvailability.objects.none()

@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics based on user role"""
    user = request.user
    stats = {}
    
    # Calculer la semaine courante
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    if user.role == 'admin':
        # Statistiques administrateur
        stats = {
            'total_departments': Department.objects.count(),
            'total_programs': Program.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_students': Student.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_rooms': Room.objects.count(),
            'total_schedules': Schedule.objects.count(),
            'active_schedules_this_week': Schedule.objects.filter(
                week_start=monday, 
                week_end=sunday,
                is_active=True
            ).count(),
            'room_utilization_rate': 75.5,  # Placeholder
            'teacher_workload_average': 18.2,  # Placeholder
        }
        
    elif user.role == 'teacher':
        # Statistiques enseignant
        try:
            teacher = Teacher.objects.get(user=user)
            weekly_schedules = Schedule.objects.filter(
                teacher=teacher,
                week_start=monday,
                week_end=sunday,
                is_active=True
            )
            
            total_minutes = sum([
                (datetime.combine(datetime.today(), schedule.end_time) - 
                 datetime.combine(datetime.today(), schedule.start_time)).seconds // 60
                for schedule in weekly_schedules
            ])
            
            stats = {
                'weekly_sessions': weekly_schedules.count(),
                'weekly_hours': total_minutes / 60.0,
                'total_subjects_taught': teacher.subjects.count(),
                'workload_percentage': min((total_minutes / 60.0) / 20 * 100, 100),  # Sur 20h max
            }
        except Teacher.DoesNotExist:
            stats = {
                'weekly_sessions': 0,
                'weekly_hours': 0,
                'total_subjects_taught': 0,
                'workload_percentage': 0,
            }
            
    elif user.role == 'student':
        # Statistiques étudiant
        try:
            student = Student.objects.get(user=user)
            weekly_schedules = Schedule.objects.filter(
                program=student.program,
                week_start=monday,
                week_end=sunday,
                is_active=True
            )
            
            total_minutes = sum([
                (datetime.combine(datetime.today(), schedule.end_time) - 
                 datetime.combine(datetime.today(), schedule.start_time)).seconds // 60
                for schedule in weekly_schedules
            ])
            
            stats = {
                'program': student.program.name,
                'weekly_sessions': weekly_schedules.count(),
                'weekly_hours': total_minutes / 60.0,
            }
        except Student.DoesNotExist:
            stats = {
                'program': 'N/A',
                'weekly_sessions': 0,
                'weekly_hours': 0,
            }
            
    elif user.role == 'department_head':
        # Statistiques chef de département
        if user.department:
            stats = {
                'department_programs': Program.objects.filter(department=user.department).count(),
                'department_teachers': Teacher.objects.filter(user__department=user.department).count(),
                'department_students': Student.objects.filter(program__department=user.department).count(),
                'department_subjects': Subject.objects.filter(department=user.department).count(),
                'department_rooms': Room.objects.filter(department=user.department).count(),
            }
        else:
            stats = {
                'department_programs': 0,
                'department_teachers': 0,
                'department_students': 0,
                'department_subjects': 0,
                'department_rooms': 0,
            }
            
    elif user.role == 'program_head':
        # Statistiques chef de filière
        if user.program:
            stats = {
                'program_students': Student.objects.filter(program=user.program).count(),
                'program_subjects': Subject.objects.filter(program=user.program).count(),
            }
        else:
            stats = {
                'program_students': 0,
                'program_subjects': 0,
            }
    
    return Response(stats)