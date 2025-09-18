from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Schedule, Absence, MakeupSession
from .serializers import ScheduleSerializer, AbsenceSerializer, MakeupSessionSerializer
from .utils import check_conflicts, get_available_rooms
from core.models import Program, Teacher, Room

class ScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program', 'teacher', 'room', 'subject', 'day_of_week', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Schedule.objects.all()
        
        if user.role == 'admin':
            return queryset
        elif user.role == 'department_head':
            return queryset.filter(program__department=user.department)
        elif user.role == 'program_head':
            return queryset.filter(program=user.program)
        elif user.role == 'teacher':
            return queryset.filter(teacher__user=user)
        elif user.role == 'student':
            return queryset.filter(program=user.student.program)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Schedule.objects.all()
        
        if user.role == 'admin':
            return queryset
        elif user.role == 'department_head':
            return queryset.filter(program__department=user.department)
        elif user.role == 'program_head':
            return queryset.filter(program=user.program)
        elif user.role == 'teacher':
            return queryset.filter(teacher__user=user)
        
        return queryset.none()

@api_view(['POST'])
def check_schedule_conflicts(request):
    """Check for conflicts before creating/updating a schedule"""
    data = request.data
    conflicts = check_conflicts(
        teacher_id=data.get('teacher'),
        room_id=data.get('room'),
        day_of_week=data.get('day_of_week'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        week_start=data.get('week_start'),
        week_end=data.get('week_end'),
        exclude_id=data.get('schedule_id')
    )
    
    return Response({
        'has_conflicts': len(conflicts) > 0,
        'conflicts': conflicts
    })

@api_view(['GET'])
def get_schedule_by_week(request):
    """Get schedule for a specific week formatted for frontend"""
    week_start = request.GET.get('week_start')
    program_id = request.GET.get('program_id')
    teacher_id = request.GET.get('teacher_id')
    room_id = request.GET.get('room_id')
    subject_id = request.GET.get('subject_id')
    
    if not week_start:
        return Response({'error': 'week_start parameter required'}, status=400)
    
    try:
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        week_end_date = week_start_date + timedelta(days=6)
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    
    # Base queryset
    queryset = Schedule.objects.filter(
        week_start=week_start_date,
        week_end=week_end_date,
        is_active=True
    ).select_related('subject', 'teacher__user', 'room', 'program')
    
    # Apply filters based on parameters
    if program_id:
        queryset = queryset.filter(program_id=program_id)
    if teacher_id:
        queryset = queryset.filter(teacher_id=teacher_id)
    if room_id:
        queryset = queryset.filter(room_id=room_id)
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    
    # Apply user role permissions
    user = request.user
    if user.role == 'department_head':
        queryset = queryset.filter(program__department=user.department)
    elif user.role == 'program_head':
        queryset = queryset.filter(program=user.program)
    elif user.role == 'teacher':
        queryset = queryset.filter(teacher__user=user)
    elif user.role == 'student':
        try:
            queryset = queryset.filter(program=user.student.program)
        except:
            queryset = queryset.none()
    
    # Organize data by days
    days_data = []
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    total_sessions = 0
    total_minutes = 0
    
    for day_index in range(7):
        current_date = week_start_date + timedelta(days=day_index)
        day_schedules = []
        
        # Get schedules for this day
        for schedule in queryset.filter(day_of_week=day_index):
            total_sessions += 1
            duration_minutes = (datetime.combine(datetime.today(), schedule.end_time) - 
                              datetime.combine(datetime.today(), schedule.start_time)).seconds // 60
            total_minutes += duration_minutes
            
            # Create schedule data structure matching frontend expectations
            schedule_data = {
                'id': schedule.id,
                'title': schedule.title,
                'subject_name': schedule.subject.name,
                'subject_code': schedule.subject.code,
                'teacher_name': schedule.teacher.user.get_full_name(),
                'room_name': schedule.room.name,
                'room_capacity': schedule.room.capacity,
                'time_slot_info': {
                    'id': schedule.id,  # Using schedule id as time slot id
                    'day_of_week': schedule.day_of_week,
                    'day_display': schedule.get_day_of_week_display(),
                    'start_time': schedule.start_time.strftime('%H:%M'),
                    'end_time': schedule.end_time.strftime('%H:%M'),
                    'duration_minutes': duration_minutes
                },
                'programs_list': [schedule.program.name],
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': current_date.strftime('%Y-%m-%d'),
                'duration_minutes': duration_minutes,
                'student_count': getattr(schedule.program, 'student_count', 0),
                'is_room_suitable': True,  # Add logic here if needed
                'is_cancelled': not schedule.is_active,
                'is_makeup': False,  # Add logic here if needed
                'notes': schedule.notes
            }
            day_schedules.append(schedule_data)
        
        # Sort schedules by start time
        day_schedules.sort(key=lambda x: x['time_slot_info']['start_time'])
        
        days_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_name': day_names[day_index],
            'schedules': day_schedules
        })
    
    # Calculate total hours
    total_hours = total_minutes / 60.0
    
    # Response data structure matching frontend expectations
    response_data = {
        'week_start': week_start_date.strftime('%Y-%m-%d'),
        'week_end': week_end_date.strftime('%Y-%m-%d'),
        'days': days_data,
        'total_sessions': total_sessions,
        'total_hours': total_hours
    }
    
    return Response(response_data)

# Absence Views
class AbsenceListCreateView(generics.ListCreateAPIView):
    serializer_class = AbsenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['absence_type', 'reason', 'is_approved']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Absence.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Absence.objects.filter(
                Q(teacher__user__department=user.department) |
                Q(program__department=user.department)
            )
        elif user.role == 'teacher':
            return Absence.objects.filter(teacher__user=user)
        return Absence.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AbsenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AbsenceSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Absence.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return Absence.objects.filter(
                Q(teacher__user__department=user.department) |
                Q(program__department=user.department)
            )
        elif user.role == 'teacher':
            return Absence.objects.filter(teacher__user=user)
        return Absence.objects.none()

# Makeup Session Views
class MakeupSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = MakeupSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MakeupSession.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return MakeupSession.objects.filter(
                original_schedule__program__department=user.department
            )
        elif user.role == 'teacher':
            return MakeupSession.objects.filter(original_schedule__teacher__user=user)
        return MakeupSession.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

class MakeupSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MakeupSessionSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MakeupSession.objects.all()
        elif user.role in ['department_head', 'program_head']:
            return MakeupSession.objects.filter(
                original_schedule__program__department=user.department
            )
        elif user.role == 'teacher':
            return MakeupSession.objects.filter(original_schedule__teacher__user=user)
        return MakeupSession.objects.none()

@api_view(['POST'])
def approve_makeup(request, pk):
    """Approve or reject makeup session"""
    try:
        makeup = MakeupSession.objects.get(pk=pk)
        action = request.data.get('action')  # 'approve' or 'reject'
        
        if action == 'approve':
            makeup.status = 'approved'
            makeup.approved_by = request.user
            message = 'Session de rattrapage approuvée'
        elif action == 'reject':
            makeup.status = 'rejected'
            makeup.approved_by = request.user
            message = 'Session de rattrapage rejetée'
        else:
            return Response({'error': 'Action invalide'}, status=400)
        
        makeup.save()
        
        return Response({
            'message': message,
            'makeup': MakeupSessionSerializer(makeup).data
        })
    
    except MakeupSession.DoesNotExist:
        return Response({'error': 'Session non trouvée'}, status=404)

@api_view(['GET'])
def available_rooms(request):
    """Get available rooms for a specific time slot"""
    day_of_week = request.GET.get('day_of_week')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    week_start = request.GET.get('week_start')
    week_end = request.GET.get('week_end')
    room_type = request.GET.get('room_type')
    
    if not all([day_of_week, start_time, end_time, week_start, week_end]):
        return Response({'error': 'Paramètres manquants'}, status=400)
    
    available = get_available_rooms(
        day_of_week=int(day_of_week),
        start_time=start_time,
        end_time=end_time,
        week_start=week_start,
        week_end=week_end,
        room_type=room_type
    )
    
    return Response(available)
