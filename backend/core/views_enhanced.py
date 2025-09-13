# views.py - Vues API améliorées pour AppGET
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, List

from .models import (
    Department, Program, Room, Subject, Teacher, Student,
    TimeSlot, Schedule, ExcelImportLog, TimetableGeneration
)
from .serializers_enhanced import (
    DepartmentSerializer, ProgramSerializer, RoomSerializer, SubjectSerializer,
    TeacherSerializer, StudentSerializer, TimeSlotSerializer,
    ScheduleListSerializer, ScheduleDetailSerializer, ScheduleCreateUpdateSerializer,
    StudentScheduleViewSerializer, TeacherScheduleViewSerializer, RoomScheduleViewSerializer,
    ExcelImportLogSerializer, TimetableGenerationSerializer, DashboardStatsSerializer
)
from .permissions import IsAdminOrReadOnly, IsTeacherOrAdmin, IsOwnerOrAdmin
from .import_excel import import_excel_file
from .timetable_solver import generate_timetable_for_programs
from .export_utils import export_schedule_to_pdf, export_schedule_to_excel


# ===== PERMISSIONS PERSONNALISÉES =====

class RoleBasedPermission(permissions.BasePermission):
    """Permission basée sur les rôles utilisateur"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Admin a tous les droits
        if user_role == 'admin':
            return True
        
        # Actions en lecture seule pour enseignants et étudiants
        if request.method in permissions.SAFE_METHODS:
            return user_role in ['teacher', 'student']
        
        # Actions d'écriture seulement pour admin
        return user_role == 'admin'


class TeacherPermission(permissions.BasePermission):
    """Permission pour les enseignants"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher']


class StudentPermission(permissions.BasePermission):
    """Permission pour les étudiants"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher', 'student']


# ===== VIEWSETS PRINCIPAUX =====

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des départements"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [RoleBasedPermission]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques d'un département"""
        department = self.get_object()
        
        stats = {
            'total_programs': department.programs.filter(is_active=True).count(),
            'total_teachers': department.teachers.filter(is_available=True).count(),
            'total_rooms': department.rooms.filter(is_available=True).count(),
            'total_subjects': department.subjects.filter(is_active=True).count(),
            'total_students': sum([
                program.students.filter(is_active=True).count() 
                for program in department.programs.filter(is_active=True)
            ])
        }
        
        return Response(stats)


class ProgramViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des programmes/filières"""
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [RoleBasedPermission]
    filterset_fields = ['department', 'level', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['department__name', 'level', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par rôle utilisateur
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'student':
                # Étudiants ne voient que leur programme
                try:
                    student = Student.objects.get(user=self.request.user)
                    queryset = queryset.filter(id=student.program.id)
                except Student.DoesNotExist:
                    queryset = queryset.none()
            elif self.request.user.role == 'teacher':
                # Enseignants voient les programmes où ils enseignent
                try:
                    teacher = Teacher.objects.get(user=self.request.user)
                    program_ids = teacher.subjects.values_list('programs', flat=True)
                    queryset = queryset.filter(id__in=program_ids)
                except Teacher.DoesNotExist:
                    pass
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Emploi du temps d'un programme"""
        program = self.get_object()
        week_start = request.query_params.get('week_start')
        
        # Calculer les dates de la semaine
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        # Récupérer les emplois du temps
        schedules = Schedule.objects.filter(
            programs=program,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True,
            is_cancelled=False
        ).select_related('subject', 'teacher__user', 'room', 'time_slot')
        
        serializer = ScheduleListSerializer(schedules, many=True)
        return Response({
            'program': self.get_serializer(program).data,
            'week_start': start_date,
            'week_end': end_date,
            'schedules': serializer.data
        })


class RoomViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des salles"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [RoleBasedPermission]
    filterset_fields = ['department', 'room_type', 'is_available']
    search_fields = ['name', 'code', 'building', 'equipment']
    ordering_fields = ['name', 'capacity', 'room_type', 'created_at']
    ordering = ['building', 'name']
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Vérifier la disponibilité d'une salle"""
        room = self.get_object()
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Récupérer les réservations pour cette date
        schedules = Schedule.objects.filter(
            room=room,
            start_date__lte=check_date,
            end_date__gte=check_date,
            is_active=True,
            is_cancelled=False
        ).select_related('time_slot', 'subject', 'teacher__user')
        
        occupied_slots = []
        for schedule in schedules:
            occupied_slots.append({
                'time_slot': schedule.time_slot.id,
                'time_display': str(schedule.time_slot),
                'subject': schedule.subject.name,
                'teacher': schedule.teacher.user.get_full_name(),
                'title': schedule.title
            })
        
        # Récupérer tous les créneaux disponibles
        all_slots = TimeSlot.objects.filter(is_active=True)
        occupied_slot_ids = [slot['time_slot'] for slot in occupied_slots]
        free_slots = all_slots.exclude(id__in=occupied_slot_ids)
        
        return Response({
            'room': self.get_serializer(room).data,
            'date': check_date,
            'occupied_slots': occupied_slots,
            'free_slots': [{'id': slot.id, 'display': str(slot)} for slot in free_slots],
            'utilization_rate': round((len(occupied_slots) / len(all_slots)) * 100, 2) if all_slots else 0
        })
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Emploi du temps d'une salle"""
        room = self.get_object()
        week_start = request.query_params.get('week_start')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        schedules = Schedule.objects.filter(
            room=room,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True
        ).select_related('subject', 'teacher__user', 'time_slot')
        
        serializer = RoomScheduleViewSerializer(schedules, many=True)
        return Response({
            'room': self.get_serializer(room).data,
            'week_start': start_date,
            'week_end': end_date,
            'schedules': serializer.data
        })


class TeacherViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des enseignants"""
    queryset = Teacher.objects.select_related('user').prefetch_related('subjects', 'departments')
    serializer_class = TeacherSerializer
    permission_classes = [TeacherPermission]
    filterset_fields = ['teacher_type', 'is_available', 'departments']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'specialization']
    ordering_fields = ['user__last_name', 'teacher_type', 'created_at']
    ordering = ['user__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les enseignants ne voient que leurs propres données
        if hasattr(self.request.user, 'role') and self.request.user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=self.request.user)
                queryset = queryset.filter(id=teacher.id)
            except Teacher.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Emploi du temps d'un enseignant"""
        teacher = self.get_object()
        week_start = request.query_params.get('week_start')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        schedules = Schedule.objects.filter(
            teacher=teacher,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True
        ).select_related('subject', 'room', 'time_slot').prefetch_related('programs')
        
        serializer = TeacherScheduleViewSerializer(schedules, many=True)
        return Response({
            'teacher': self.get_serializer(teacher).data,
            'week_start': start_date,
            'week_end': end_date,
            'schedules': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def workload(self, request, pk=None):
        """Charge de travail d'un enseignant"""
        teacher = self.get_object()
        
        # Charge actuelle (cette semaine)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        current_schedules = Schedule.objects.filter(
            teacher=teacher,
            start_date__lte=week_end,
            end_date__gte=week_start,
            is_active=True,
            is_cancelled=False
        )
        
        current_hours = sum([schedule.duration_minutes for schedule in current_schedules]) / 60
        
        # Charge du mois
        month_start = today.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        
        monthly_schedules = Schedule.objects.filter(
            teacher=teacher,
            start_date__gte=month_start,
            end_date__lte=month_end,
            is_active=True,
            is_cancelled=False
        )
        
        monthly_hours = sum([schedule.duration_minutes for schedule in monthly_schedules]) / 60
        
        return Response({
            'teacher': teacher.user.get_full_name(),
            'current_week': {
                'hours': round(current_hours, 2),
                'sessions': current_schedules.count(),
                'utilization_rate': round((current_hours / teacher.max_hours_per_week) * 100, 2)
            },
            'current_month': {
                'hours': round(monthly_hours, 2),
                'sessions': monthly_schedules.count(),
                'average_per_week': round(monthly_hours / 4, 2)
            },
            'limits': {
                'max_hours_per_week': teacher.max_hours_per_week,
                'max_hours_per_day': teacher.max_hours_per_day
            }
        })


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des étudiants"""
    queryset = Student.objects.select_related('user', 'program').all()
    serializer_class = StudentSerializer
    permission_classes = [RoleBasedPermission]
    filterset_fields = ['program', 'enrollment_year', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'student_id']
    ordering_fields = ['user__last_name', 'student_id', 'enrollment_year']
    ordering = ['program__name', 'user__last_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les étudiants ne voient que leurs propres données
        if hasattr(self.request.user, 'role') and self.request.user.role == 'student':
            try:
                student = Student.objects.get(user=self.request.user)
                queryset = queryset.filter(id=student.id)
            except Student.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Emploi du temps d'un étudiant"""
        student = self.get_object()
        week_start = request.query_params.get('week_start')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        # Emploi du temps du programme de l'étudiant
        schedules = Schedule.objects.filter(
            programs=student.program,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True,
            is_cancelled=False
        ).select_related('subject', 'teacher__user', 'room', 'time_slot')
        
        serializer = StudentScheduleViewSerializer(schedules, many=True)
        return Response({
            'student': self.get_serializer(student).data,
            'week_start': start_date,
            'week_end': end_date,
            'schedules': serializer.data
        })


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des emplois du temps"""
    queryset = Schedule.objects.select_related(
        'subject', 'teacher__user', 'room', 'time_slot', 'created_by'
    ).prefetch_related('programs').all()
    permission_classes = [RoleBasedPermission]
    filterset_fields = ['subject', 'teacher', 'room', 'is_active', 'is_cancelled']
    search_fields = ['title', 'subject__name', 'teacher__user__first_name', 'teacher__user__last_name']
    ordering_fields = ['start_date', 'time_slot__day_of_week', 'time_slot__start_time']
    ordering = ['start_date', 'time_slot__day_of_week', 'time_slot__start_time']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ScheduleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ScheduleCreateUpdateSerializer
        return ScheduleDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par rôle
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'student':
                # Étudiants ne voient que leur emploi du temps
                try:
                    student = Student.objects.get(user=self.request.user)
                    queryset = queryset.filter(programs=student.program)
                except Student.DoesNotExist:
                    queryset = queryset.none()
            elif self.request.user.role == 'teacher':
                # Enseignants ne voient que leurs cours
                try:
                    teacher = Teacher.objects.get(user=self.request.user)
                    queryset = queryset.filter(teacher=teacher)
                except Teacher.DoesNotExist:
                    queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """Emploi du temps hebdomadaire"""
        week_start = request.query_params.get('week_start')
        program_id = request.query_params.get('program')
        teacher_id = request.query_params.get('teacher')
        room_id = request.query_params.get('room')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        # Filtres
        queryset = self.get_queryset().filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True
        )
        
        if program_id:
            queryset = queryset.filter(programs__id=program_id)
        if teacher_id:
            queryset = queryset.filter(teacher__id=teacher_id)
        if room_id:
            queryset = queryset.filter(room__id=room_id)
        
        # Organiser par jour
        days_data = []
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            day_schedules = queryset.filter(
                time_slot__day_of_week=day
            ).order_by('time_slot__start_time')
            
            days_data.append({
                'date': current_date,
                'day_name': current_date.strftime('%A'),
                'schedules': ScheduleListSerializer(day_schedules, many=True).data
            })
        
        total_sessions = queryset.count()
        total_hours = sum([schedule.duration_minutes for schedule in queryset]) / 60
        
        return Response({
            'week_start': start_date,
            'week_end': end_date,
            'days': days_data,
            'total_sessions': total_sessions,
            'total_hours': round(total_hours, 2)
        })


# ===== VUES SPÉCIALISÉES =====

class DashboardView(APIView):
    """Vue pour les statistiques du tableau de bord"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user_role = getattr(request.user, 'role', None)
        
        if user_role == 'admin':
            return self._get_admin_dashboard()
        elif user_role == 'teacher':
            return self._get_teacher_dashboard()
        elif user_role == 'student':
            return self._get_student_dashboard()
        else:
            return Response({'error': 'Rôle utilisateur non reconnu'}, status=400)
    
    def _get_admin_dashboard(self):
        """Dashboard administrateur"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Statistiques générales
        stats = {
            'total_departments': Department.objects.filter(is_active=True).count(),
            'total_programs': Program.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(is_available=True).count(),
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_rooms': Room.objects.filter(is_available=True).count(),
            'total_subjects': Subject.objects.filter(is_active=True).count(),
            'total_schedules': Schedule.objects.filter(is_active=True).count(),
            'active_schedules_this_week': Schedule.objects.filter(
                start_date__lte=week_end,
                end_date__gte=week_start,
                is_active=True,
                is_cancelled=False
            ).count()
        }
        
        # Taux d'utilisation des salles
        total_possible_slots = Room.objects.filter(is_available=True).count() * TimeSlot.objects.filter(is_active=True).count()
        used_slots = Schedule.objects.filter(
            start_date__lte=week_end,
            end_date__gte=week_start,
            is_active=True,
            is_cancelled=False
        ).count()
        
        stats['room_utilization_rate'] = round((used_slots / total_possible_slots) * 100, 2) if total_possible_slots > 0 else 0
        
        # Charge moyenne des enseignants
        teacher_workloads = []
        for teacher in Teacher.objects.filter(is_available=True):
            weekly_minutes = Schedule.objects.filter(
                teacher=teacher,
                start_date__lte=week_end,
                end_date__gte=week_start,
                is_active=True,
                is_cancelled=False
            ).aggregate(total=Sum('duration_minutes'))['total'] or 0
            
            teacher_workloads.append(weekly_minutes / 60)
        
        stats['teacher_workload_average'] = round(sum(teacher_workloads) / len(teacher_workloads), 2) if teacher_workloads else 0
        
        return Response(stats)
    
    def _get_teacher_dashboard(self):
        """Dashboard enseignant"""
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Cours de cette semaine
            weekly_schedules = Schedule.objects.filter(
                teacher=teacher,
                start_date__lte=week_end,
                end_date__gte=week_start,
                is_active=True,
                is_cancelled=False
            )
            
            # Prochains cours
            upcoming_schedules = Schedule.objects.filter(
                teacher=teacher,
                start_date__gte=today,
                is_active=True,
                is_cancelled=False
            ).order_by('start_date', 'time_slot__start_time')[:5]
            
            stats = {
                'weekly_sessions': weekly_schedules.count(),
                'weekly_hours': round(sum([s.duration_minutes for s in weekly_schedules]) / 60, 2),
                'upcoming_sessions': TeacherScheduleViewSerializer(upcoming_schedules, many=True).data,
                'total_subjects': teacher.subjects.filter(is_active=True).count(),
                'workload_percentage': round((sum([s.duration_minutes for s in weekly_schedules]) / 60) / teacher.max_hours_per_week * 100, 2)
            }
            
            return Response(stats)
            
        except Teacher.DoesNotExist:
            return Response({'error': 'Profil enseignant introuvable'}, status=404)
    
    def _get_student_dashboard(self):
        """Dashboard étudiant"""
        try:
            student = Student.objects.get(user=self.request.user)
            today = timezone.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Cours de cette semaine
            weekly_schedules = Schedule.objects.filter(
                programs=student.program,
                start_date__lte=week_end,
                end_date__gte=week_start,
                is_active=True,
                is_cancelled=False
            )
            
            # Prochains cours
            upcoming_schedules = Schedule.objects.filter(
                programs=student.program,
                start_date__gte=today,
                is_active=True,
                is_cancelled=False
            ).order_by('start_date', 'time_slot__start_time')[:5]
            
            stats = {
                'program': student.program.name,
                'weekly_sessions': weekly_schedules.count(),
                'weekly_hours': round(sum([s.duration_minutes for s in weekly_schedules]) / 60, 2),
                'upcoming_sessions': StudentScheduleViewSerializer(upcoming_schedules, many=True).data,
                'total_subjects': student.program.subjects.filter(is_active=True).count()
            }
            
            return Response(stats)
            
        except Student.DoesNotExist:
            return Response({'error': 'Profil étudiant introuvable'}, status=404)


class ExcelImportView(APIView):
    """Vue pour l'importation de fichiers Excel"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Vérifier les permissions (admin seulement)
        if getattr(request.user, 'role', None) != 'admin':
            return Response(
                {'error': 'Seuls les administrateurs peuvent importer des fichiers Excel'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response({'error': 'Aucun fichier fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        excel_file = request.FILES['file']
        
        # Valider le type de fichier
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': 'Format de fichier non supporté. Utilisez .xlsx ou .xls'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Sauvegarder le fichier temporairement
            file_path = default_storage.save(
                f'temp_excel/{excel_file.name}',
                excel_file
            )
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Importer les données
            result = import_excel_file(full_path, request.user.id)
            
            # Nettoyer le fichier temporaire
            default_storage.delete(file_path)
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Importation réussie',
                    'stats': result['stats'],
                    'log_id': result['log_id']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result['error'],
                    'log_id': result.get('log_id')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de l\'importation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TimetableGenerationView(APIView):
    """Vue pour la génération automatique d'emplois du temps"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Vérifier les permissions (admin seulement)
        if getattr(request.user, 'role', None) != 'admin':
            return Response(
                {'error': 'Seuls les administrateurs peuvent générer des emplois du temps'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Paramètres
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        program_ids = request.data.get('program_ids', [])
        
        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'Dates de début et fin requises'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                return Response(
                    {'error': 'La date de fin doit être postérieure à la date de début'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Générer l'emploi du temps
            result = generate_timetable_for_programs(
                request.user.id,
                start_date,
                end_date,
                program_ids if program_ids else None
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': 'Emploi du temps généré avec succès',
                    'stats': result['stats'],
                    'generation_id': result['generation_id']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result['error'],
                    'generation_id': result.get('generation_id')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            return Response(
                {'error': 'Format de date invalide (utilisez YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportScheduleView(APIView):
    """Vue pour l'export d'emplois du temps en PDF/Excel"""
    permission_classes = [StudentPermission]
    
    def get(self, request):
        export_format = request.query_params.get('format', 'pdf')  # pdf ou excel
        export_type = request.query_params.get('type', 'personal')  # personal, program, teacher, room
        target_id = request.query_params.get('id')
        week_start = request.query_params.get('week_start')
        
        if week_start:
            start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        else:
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
        
        end_date = start_date + timedelta(days=6)
        
        try:
            # Récupérer les données selon le type d'export
            if export_type == 'personal':
                schedules, title = self._get_personal_schedule(request.user, start_date, end_date)
            elif export_type == 'program' and target_id:
                program = get_object_or_404(Program, id=target_id)
                schedules = Schedule.objects.filter(
                    programs=program,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    is_active=True,
                    is_cancelled=False
                )
                title = f"Emploi du temps - {program.name}"
            elif export_type == 'teacher' and target_id:
                teacher = get_object_or_404(Teacher, id=target_id)
                schedules = Schedule.objects.filter(
                    teacher=teacher,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    is_active=True,
                    is_cancelled=False
                )
                title = f"Emploi du temps - {teacher.user.get_full_name()}"
            elif export_type == 'room' and target_id:
                room = get_object_or_404(Room, id=target_id)
                schedules = Schedule.objects.filter(
                    room=room,
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                    is_active=True,
                    is_cancelled=False
                )
                title = f"Planning salle - {room.name}"
            else:
                return Response({'error': 'Type d\'export invalide'}, status=400)
            
            # Générer le fichier
            if export_format == 'pdf':
                file_content, filename = export_schedule_to_pdf(schedules, title, start_date, end_date)
                content_type = 'application/pdf'
            else:
                file_content, filename = export_schedule_to_excel(schedules, title, start_date, end_date)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de l\'export: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_personal_schedule(self, user, start_date, end_date):
        """Récupérer l'emploi du temps personnel selon le rôle"""
        if user.role == 'student':
            student = get_object_or_404(Student, user=user)
            schedules = Schedule.objects.filter(
                programs=student.program,
                start_date__lte=end_date,
                end_date__gte=start_date,
                is_active=True,
                is_cancelled=False
            )
            title = f"Mon emploi du temps - {student.program.name}"
        elif user.role == 'teacher':
            teacher = get_object_or_404(Teacher, user=user)
            schedules = Schedule.objects.filter(
                teacher=teacher,
                start_date__lte=end_date,
                end_date__gte=start_date,
                is_active=True,
                is_cancelled=False
            )
            title = f"Mon emploi du temps - {teacher.user.get_full_name()}"
        else:
            # Admin peut voir tous les emplois du temps
            schedules = Schedule.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date,
                is_active=True,
                is_cancelled=False
            )
            title = "Emploi du temps général"
        
        return schedules, title


# ===== VIEWSETS POUR LES LOGS =====

class ExcelImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les logs d'importation Excel"""
    queryset = ExcelImportLog.objects.all()
    serializer_class = ExcelImportLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-import_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les non-admins ne voient que leurs propres imports
        if getattr(self.request.user, 'role', None) != 'admin':
            queryset = queryset.filter(imported_by=self.request.user)
        
        return queryset


class TimetableGenerationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les logs de génération d'emploi du temps"""
    queryset = TimetableGeneration.objects.all()
    serializer_class = TimetableGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-generation_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Les non-admins ne voient que leurs propres générations
        if getattr(self.request.user, 'role', None) != 'admin':
            queryset = queryset.filter(generated_by=self.request.user)
        
        return queryset
