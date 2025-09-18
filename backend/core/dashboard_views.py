from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Department, Program, Room, Subject, Teacher, Student
from schedule.models import Schedule


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """Dashboard pour les administrateurs"""
    period = request.GET.get('period', 'week')
    
    # Calculer la période
    today = timezone.now().date()
    if period == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'month':
        start_date = today.replace(day=1)
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)
    else:  # year
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    
    # Statistiques générales
    total_departments = Department.objects.count()
    total_programs = Program.objects.count()
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    total_subjects = Subject.objects.count()
    
    # Statistiques des emplois du temps
    total_schedules = Schedule.objects.filter(
        week_start__lte=end_date,
        week_end__gte=start_date,
        is_active=True
    ).count()
    
    # Programmes les plus actifs
    programs_stats = Program.objects.annotate(
        schedules_count=Count('schedules')
    ).order_by('-schedules_count')[:5]
    
    programs_data = [{
        'id': program.id,
        'name': program.name,
        'level': program.get_level_display(),
        'department': program.department.name,
        'schedules_count': program.schedules_count,
        'students_count': program.students.count()
    } for program in programs_stats]
    
    return Response({
        'stats': {
            'departments': total_departments,
            'programs': total_programs,
            'teachers': total_teachers,
            'students': total_students,
            'rooms': total_rooms,
            'subjects': total_subjects,
            'schedules': total_schedules
        },
        'programs': programs_data,
        'period': period
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_dashboard(request):
    """Dashboard pour les enseignants"""
    user = request.user
    
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        return Response({
            'error': 'Profil enseignant non trouvé',
            'message': 'Votre compte enseignant n\'est pas encore configuré. Contactez l\'administrateur.',
            'user_info': {
                'name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }, status=404)
    
    # Calculer les dates de la semaine courante
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Emplois du temps de la semaine
    schedules_this_week = Schedule.objects.filter(
        teacher=teacher,
        week_start=week_start,
        is_active=True
    ).select_related('subject', 'room', 'program').order_by('day_of_week', 'start_time')
    
    schedules_data = [{
        'id': schedule.id,
        'title': schedule.title,
        'subject': schedule.subject.name,
        'room': schedule.room.name,
        'program': schedule.program.name,
        'day_of_week': schedule.get_day_of_week_display(),
        'start_time': schedule.start_time.strftime('%H:%M'),
        'end_time': schedule.end_time.strftime('%H:%M'),
        'status': 'scheduled'
    } for schedule in schedules_this_week]
    
    # Statistiques
    total_schedules = Schedule.objects.filter(teacher=teacher, is_active=True).count()
    subjects_count = teacher.subjects.count()
    programs_count = Program.objects.filter(schedules__teacher=teacher).distinct().count()
    
    # Matières enseignées
    subjects_data = [{
        'id': subject.id,
        'name': subject.name,
        'code': subject.code,
        'department': subject.department.name
    } for subject in teacher.subjects.all()]
    
    return Response({
        'teacher': {
            'id': teacher.id,
            'name': teacher.user.full_name,
            'email': teacher.user.email,
            'specialization': teacher.specialization or 'Non spécifiée'
        },
        'stats': {
            'total_schedules': total_schedules,
            'subjects_count': subjects_count,
            'programs_count': programs_count,
            'schedules_this_week': len(schedules_data)
        },
        'schedules_this_week': schedules_data,
        'subjects': subjects_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """Dashboard pour les étudiants"""
    user = request.user
    
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({
            'error': 'Profil étudiant non trouvé',
            'message': 'Votre compte étudiant n\'est pas encore configuré. Contactez l\'administrateur.',
            'user_info': {
                'name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }, status=404)
    
    # Calculer les dates de la semaine courante
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Emplois du temps de la semaine
    schedules_this_week = Schedule.objects.filter(
        program=student.program,
        week_start=week_start,
        is_active=True
    ).select_related('subject', 'teacher__user', 'room').order_by('day_of_week', 'start_time')
    
    schedules_data = [{
        'id': schedule.id,
        'title': schedule.title,
        'subject': schedule.subject.name,
        'teacher': schedule.teacher.user.full_name,
        'room': schedule.room.name,
        'day_of_week': schedule.get_day_of_week_display(),
        'start_time': schedule.start_time.strftime('%H:%M'),
        'end_time': schedule.end_time.strftime('%H:%M'),
        'type': schedule.subject.course_type or 'Cours'
    } for schedule in schedules_this_week]
    
    # Statistiques
    total_schedules = Schedule.objects.filter(
        program=student.program, 
        is_active=True
    ).count()
    
    return Response({
        'student': {
            'id': student.id,
            'name': student.user.full_name,
            'email': student.user.email,
            'program': {
                'name': student.program.name,
                'level': student.program.get_level_display(),
                'department': student.program.department.name
            },
            'student_id': student.student_id
        },
        'stats': {
            'total_schedules': total_schedules,
            'schedules_this_week': len(schedules_data)
        },
        'schedules_this_week': schedules_data
    })
