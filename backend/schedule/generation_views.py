from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta, time
import random

from core.models import Program, Teacher, Room, Subject
from schedule.models import Schedule
from authentication.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_timetable(request):
    """
    Génère automatiquement un emploi du temps pour les programmes sélectionnés
    """
    # Debug : afficher les données reçues
    print(f"[DEBUG] Données reçues: {request.data}")
    print(f"[DEBUG] Méthode: {request.method}")
    print(f"[DEBUG] Content-Type: {request.content_type}")
    
    data = request.data
    # Supporter les deux formats pour compatibilité
    selected_programs = data.get('programs', []) or data.get('program_ids', [])
    
    print(f"[DEBUG] Programmes sélectionnés: {selected_programs}")
    print(f"[DEBUG] Format reçu - programs: {data.get('programs')}, program_ids: {data.get('program_ids')}")
    
    if not selected_programs:
        return Response({
            'success': False,
            'message': 'Aucun programme sélectionné',
            'debug_info': {
                'received_data': dict(request.data),
                'programs_field': data.get('programs'),
                'all_fields': list(data.keys()) if hasattr(data, 'keys') else 'No keys method'
            }
        }, status=400)
    
    try:
        generated_schedules = []
        conflicts = []
        
        # Configuration de base
        days_of_week = [0, 1, 2, 3, 4]  # Lundi à Vendredi
        time_slots = [
            (time(8, 0), time(10, 0)),   # 8h-10h
            (time(10, 15), time(12, 15)), # 10h15-12h15
            (time(14, 0), time(16, 0)),   # 14h-16h
            (time(16, 15), time(18, 15)), # 16h15-18h15
        ]
        
        # Date de début (semaine prochaine)
        today = timezone.now().date()
        week_start = today + timedelta(days=(7 - today.weekday()))
        week_end = week_start + timedelta(days=6)
        
        for program_id in selected_programs:
            try:
                program = Program.objects.get(id=program_id)
                
                # Récupérer les matières du programme
                subjects = program.subjects.all()
                
                if not subjects:
                    conflicts.append(f"Aucune matière trouvée pour le programme {program.name}")
                    continue
                
                schedules_for_program = []
                
                for subject in subjects:
                    # Trouver un enseignant disponible pour cette matière
                    available_teachers = subject.teachers.all()
                    
                    if not available_teachers:
                        conflicts.append(f"Aucun enseignant assigné à {subject.name}")
                        continue
                    
                    teacher = random.choice(available_teachers)
                    
                    # Planifier selon les heures par semaine (2-3 créneaux par matière)
                    sessions_needed = min(subject.hours_per_week // 2, 3)
                    
                    for session in range(sessions_needed):
                        # Choisir un jour et un créneau aléatoirement
                        day = random.choice(days_of_week)
                        start_time, end_time = random.choice(time_slots)
                        
                        # Trouver une salle disponible
                        available_rooms = Room.objects.filter(
                            department=program.department,
                            is_available=True
                        )
                        
                        if not available_rooms:
                            conflicts.append(f"Aucune salle disponible pour {subject.name}")
                            continue
                        
                        room = random.choice(available_rooms)
                        
                        # Vérifier les conflits
                        existing_schedule = Schedule.objects.filter(
                            day_of_week=day,
                            start_time=start_time,
                            week_start=week_start,
                            is_active=True
                        ).filter(
                            models.Q(room=room) | models.Q(teacher=teacher)
                        ).first()
                        
                        if existing_schedule:
                            conflicts.append(f"Conflit détecté pour {subject.name} le {get_day_name(day)} à {start_time}")
                            continue
                        
                        # Créer l'emploi du temps
                        schedule_title = f"{subject.name} - {program.name}"
                        if session > 0:
                            schedule_title += f" (Séance {session + 1})"
                        
                        schedule = Schedule.objects.create(
                            title=schedule_title,
                            subject=subject,
                            teacher=teacher,
                            room=room,
                            program=program,
                            day_of_week=day,
                            start_time=start_time,
                            end_time=end_time,
                            week_start=week_start,
                            week_end=week_end,
                            created_by=request.user,
                            is_active=True
                        )
                        
                        schedules_for_program.append({
                            'id': schedule.id,
                            'title': schedule.title,
                            'subject': subject.name,
                            'teacher': teacher.user.full_name,
                            'room': room.name,
                            'day': get_day_name(day),
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M')
                        })
                
                generated_schedules.extend(schedules_for_program)
                
            except Program.DoesNotExist:
                conflicts.append(f"Programme avec l'ID {program_id} non trouvé")
                continue
        
        # Statistiques
        success_count = len(generated_schedules)
        conflict_count = len(conflicts)
        
        return Response({
            'success': True,
            'message': f'Génération terminée avec succès',
            'stats': {
                'schedules_created': success_count,
                'conflicts_detected': conflict_count,
                'success_rate': f"{(success_count / (success_count + conflict_count) * 100):.1f}%" if (success_count + conflict_count) > 0 else "100%"
            },
            'schedules': generated_schedules,
            'conflicts': conflicts[:10],  # Limiter à 10 conflits pour l'affichage
            'week_info': {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la génération: {str(e)}',
            'error': str(e)
        }, status=500)


def get_day_name(day_number):
    """Convertit le numéro du jour en nom"""
    days = {
        0: 'Lundi',
        1: 'Mardi', 
        2: 'Mercredi',
        3: 'Jeudi',
        4: 'Vendredi',
        5: 'Samedi',
        6: 'Dimanche'
    }
    return days.get(day_number, f'Jour {day_number}')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generation_stats(request):
    """Retourne les statistiques de génération d'emploi du temps"""
    
    # Compter les emplois du temps récents
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    recent_schedules = Schedule.objects.filter(
        created_at__gte=week_start,
        is_active=True
    ).count()
    
    # Compter les conflits potentiels
    conflicts = 0
    # Logique de détection des conflits simplifié
    
    # Statistiques générales
    total_schedules = Schedule.objects.filter(is_active=True).count()
    total_programs = Program.objects.count()
    
    return Response({
        'recent_schedules': recent_schedules,
        'total_schedules': total_schedules,
        'conflicts': conflicts,
        'programs_count': total_programs,
        'generation_success_rate': 85.5  # Placeholder
    })
