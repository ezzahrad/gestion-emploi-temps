from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime, date
from .models import Program, Schedule
from .schedule_generator import ScheduleGenerator
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_automatic_schedule(request):
    """
    Génère automatiquement l'emploi du temps pour tous les programmes
    """
    try:
        data = request.data
        
        # Récupérer les paramètres
        week_start = datetime.strptime(data.get('week_start'), '%Y-%m-%d').date()
        week_end = datetime.strptime(data.get('week_end'), '%Y-%m-%d').date()
        replace_existing = data.get('replace_existing', False)
        program_ids = data.get('program_ids', [])  # Si vide, traiter tous les programmes
        
        # Supprimer les emplois du temps existants si demandé
        if replace_existing:
            query = Schedule.objects.filter(week_start=week_start, week_end=week_end)
            if program_ids:
                query = query.filter(program_id__in=program_ids)
            deleted_count = query.count()
            query.delete()
        else:
            deleted_count = 0
        
        # Générer les nouveaux emplois du temps
        generator = ScheduleGenerator()
        
        if program_ids:
            # Générer pour les programmes spécifiés
            programs = Program.objects.filter(id__in=program_ids)
            all_results = []
            total_schedules = 0
            all_conflicts = []
            
            for program in programs:
                result = generator.generate_schedule_for_program(
                    program, week_start, week_end, request.user
                )
                all_results.append(result)
                total_schedules += len(result['generated_schedules'])
                all_conflicts.extend(result['conflicts'])
            
            final_result = {
                'total_schedules': total_schedules,
                'total_conflicts': len(all_conflicts),
                'results_by_program': all_results,
                'conflicts': all_conflicts
            }
        else:
            # Générer pour tous les programmes
            final_result = generator.generate_full_schedule(week_start, week_end, request.user)
        
        return Response({
            'success': True,
            'message': 'Emploi du temps généré avec succès',
            'data': {
                'deleted_schedules': deleted_count,
                'created_schedules': final_result['total_schedules'],
                'conflicts': final_result['conflicts'],
                'results_by_program': final_result['results_by_program']
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la génération: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_schedule_conflicts(request):
    """
    Vérifie les conflits dans l'emploi du temps existant
    """
    try:
        data = request.data
        week_start = datetime.strptime(data.get('week_start'), '%Y-%m-%d').date()
        week_end = datetime.strptime(data.get('week_end'), '%Y-%m-%d').date()
        
        # Récupérer tous les créneaux de la période
        schedules = Schedule.objects.filter(
            week_start__lte=week_end,
            week_end__gte=week_start,
            is_active=True
        ).select_related('teacher', 'room', 'subject', 'program')
        
        conflicts = []
        
        # Vérifier les conflits d'enseignants
        teacher_schedules = {}
        for schedule in schedules:
            key = f"{schedule.teacher_id}_{schedule.day_of_week}"
            if key not in teacher_schedules:
                teacher_schedules[key] = []
            teacher_schedules[key].append(schedule)
        
        for key, teacher_schedule_list in teacher_schedules.items():
            teacher_id, day = key.split('_')
            for i, schedule1 in enumerate(teacher_schedule_list):
                for schedule2 in teacher_schedule_list[i+1:]:
                    if (schedule1.start_time < schedule2.end_time and 
                        schedule1.end_time > schedule2.start_time):
                        conflicts.append({
                            'type': 'teacher_conflict',
                            'teacher': schedule1.teacher.user.full_name,
                            'day': schedule1.get_day_of_week_display(),
                            'schedule1': {
                                'title': schedule1.title,
                                'time': f"{schedule1.start_time} - {schedule1.end_time}"
                            },
                            'schedule2': {
                                'title': schedule2.title,
                                'time': f"{schedule2.start_time} - {schedule2.end_time}"
                            }
                        })
        
        # Vérifier les conflits de salles
        room_schedules = {}
        for schedule in schedules:
            key = f"{schedule.room_id}_{schedule.day_of_week}"
            if key not in room_schedules:
                room_schedules[key] = []
            room_schedules[key].append(schedule)
        
        for key, room_schedule_list in room_schedules.items():
            room_id, day = key.split('_')
            for i, schedule1 in enumerate(room_schedule_list):
                for schedule2 in room_schedule_list[i+1:]:
                    if (schedule1.start_time < schedule2.end_time and 
                        schedule1.end_time > schedule2.start_time):
                        conflicts.append({
                            'type': 'room_conflict',
                            'room': schedule1.room.name,
                            'day': schedule1.get_day_of_week_display(),
                            'schedule1': {
                                'title': schedule1.title,
                                'time': f"{schedule1.start_time} - {schedule1.end_time}"
                            },
                            'schedule2': {
                                'title': schedule2.title,
                                'time': f"{schedule2.start_time} - {schedule2.end_time}"
                            }
                        })
        
        return Response({
            'success': True,
            'conflicts': conflicts,
            'total_conflicts': len(conflicts),
            'message': f'{len(conflicts)} conflit(s) détecté(s)'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la vérification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_schedule_statistics(request):
    """
    Retourne les statistiques de l'emploi du temps
    """
    try:
        week_start = request.GET.get('week_start')
        week_end = request.GET.get('week_end')
        
        if week_start and week_end:
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
            week_end = datetime.strptime(week_end, '%Y-%m-%d').date()
            
            schedules = Schedule.objects.filter(
                week_start__lte=week_end,
                week_end__gte=week_start,
                is_active=True
            )
        else:
            schedules = Schedule.objects.filter(is_active=True)
        
        # Statistiques par programme
        programs_stats = {}
        for schedule in schedules:
            program_name = schedule.program.name
            if program_name not in programs_stats:
                programs_stats[program_name] = {
                    'total_hours': 0,
                    'sessions_count': 0,
                    'teachers': set(),
                    'rooms': set(),
                    'subjects': set()
                }
            
            duration = (datetime.combine(date.today(), schedule.end_time) - 
                       datetime.combine(date.today(), schedule.start_time)).seconds / 3600
            
            programs_stats[program_name]['total_hours'] += duration
            programs_stats[program_name]['sessions_count'] += 1
            programs_stats[program_name]['teachers'].add(schedule.teacher.user.full_name)
            programs_stats[program_name]['rooms'].add(schedule.room.name)
            programs_stats[program_name]['subjects'].add(schedule.subject.name)
        
        # Convertir les sets en listes pour JSON
        for program in programs_stats:
            programs_stats[program]['teachers'] = list(programs_stats[program]['teachers'])
            programs_stats[program]['rooms'] = list(programs_stats[program]['rooms'])
            programs_stats[program]['subjects'] = list(programs_stats[program]['subjects'])
        
        return Response({
            'success': True,
            'statistics': {
                'total_schedules': schedules.count(),
                'programs_stats': programs_stats,
                'period': {
                    'start': week_start.isoformat() if week_start else None,
                    'end': week_end.isoformat() if week_end else None
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors du calcul des statistiques: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
