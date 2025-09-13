#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module de génération automatique des emplois du temps
Respecte toutes les contraintes académiques et de ressources
"""

import os
import django
from datetime import datetime, time, timedelta
from collections import defaultdict
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from core.models import Teacher, Room, Subject, Program
from schedule.models import Schedule
from django.core.exceptions import ValidationError
from django.db import transaction

class ScheduleGenerator:
    """Générateur intelligent d'emplois du temps"""
    
    def __init__(self):
        self.conflicts = []
        self.time_slots = self._generate_time_slots()
        self.days = [1, 2, 3, 4, 5]  # Lundi à Vendredi
        self.max_hours_per_day = 6
        self.preferred_room_types = {
            'lecture': ['amphitheater', 'lecture'],
            'td': ['td', 'lecture'],
            'lab': ['lab'],
            'exam': ['amphitheater', 'lecture', 'td']
        }
    
    def _generate_time_slots(self):
        """Génère les créneaux horaires disponibles"""
        slots = []
        start_hour = 8
        end_hour = 18
        slot_duration = 90  # 1h30 par créneau
        
        current_time = time(start_hour, 0)
        while current_time.hour < end_hour:
            end_time = (datetime.combine(datetime.today(), current_time) + 
                       timedelta(minutes=slot_duration)).time()
            
            if end_time.hour <= end_hour:
                slots.append((current_time, end_time))
            
            # Pause déjeuner 12h-14h
            if current_time.hour == 11 and current_time.minute == 30:
                current_time = time(14, 0)
            else:
                current_time = (datetime.combine(datetime.today(), current_time) + 
                               timedelta(minutes=slot_duration)).time()
        
        return slots
    
    def check_teacher_availability(self, teacher, day, start_time, end_time, week_start, week_end):
        """Vérifie la disponibilité d'un enseignant"""
        # Vérifier les créneaux existants
        existing_schedules = Schedule.objects.filter(
            teacher=teacher,
            day_of_week=day,
            week_start__lte=week_end,
            week_end__gte=week_start,
            is_active=True
        )
        
        for schedule in existing_schedules:
            if (start_time < schedule.end_time and end_time > schedule.start_time):
                return False
        
        # Vérifier la charge horaire quotidienne
        daily_hours = self._calculate_daily_hours(teacher, day, week_start, week_end)
        session_duration = (datetime.combine(datetime.today(), end_time) - 
                          datetime.combine(datetime.today(), start_time)).seconds / 3600
        
        if daily_hours + session_duration > self.max_hours_per_day:
            return False
        
        return True
    
    def check_room_availability(self, room, day, start_time, end_time, week_start, week_end):
        """Vérifie la disponibilité d'une salle"""
        return not Schedule.objects.filter(
            room=room,
            day_of_week=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
            week_start__lte=week_end,
            week_end__gte=week_start,
            is_active=True
        ).exists()
    
    def _calculate_daily_hours(self, teacher, day, week_start, week_end):
        """Calcule les heures déjà programmées pour un enseignant un jour donné"""
        schedules = Schedule.objects.filter(
            teacher=teacher,
            day_of_week=day,
            week_start__lte=week_end,
            week_end__gte=week_start,
            is_active=True
        )
        
        total_hours = 0
        for schedule in schedules:
            duration = (datetime.combine(datetime.today(), schedule.end_time) - 
                       datetime.combine(datetime.today(), schedule.start_time)).seconds / 3600
            total_hours += duration
        
        return total_hours
    
    def find_suitable_room(self, subject, day, start_time, end_time, week_start, week_end):
        """Trouve une salle adaptée au type de cours"""
        preferred_types = self.preferred_room_types.get(subject.subject_type, ['lecture'])
        
        # Chercher d'abord dans les types préférés
        for room_type in preferred_types:
            rooms = Room.objects.filter(
                room_type=room_type,
                is_available=True,
                department=subject.department
            ).order_by('-capacity')
            
            for room in rooms:
                if self.check_room_availability(room, day, start_time, end_time, week_start, week_end):
                    return room
        
        # Si aucune salle préférée, chercher dans toutes les salles du département
        rooms = Room.objects.filter(
            is_available=True,
            department=subject.department
        ).order_by('-capacity')
        
        for room in rooms:
            if self.check_room_availability(room, day, start_time, end_time, week_start, week_end):
                return room
        
        return None
    
    def generate_alternative_slot(self, teacher, subject, week_start, week_end, exclude_slots=None):
        """Trouve un créneau alternatif en cas de conflit"""
        exclude_slots = exclude_slots or []
        
        for day in self.days:
            for start_time, end_time in self.time_slots:
                slot_id = f"{day}_{start_time}_{end_time}"
                
                if slot_id in exclude_slots:
                    continue
                
                if self.check_teacher_availability(teacher, day, start_time, end_time, week_start, week_end):
                    room = self.find_suitable_room(subject, day, start_time, end_time, week_start, week_end)
                    if room:
                        return {
                            'day': day,
                            'start_time': start_time,
                            'end_time': end_time,
                            'room': room
                        }
        
        return None
    
    @transaction.atomic
    def generate_schedule_for_program(self, program, week_start, week_end, created_by):
        """Génère l'emploi du temps pour un programme donné"""
        print(f"Génération emploi du temps pour {program.name}...")
        
        # Récupérer toutes les matières du programme
        subjects = Subject.objects.filter(program=program)
        generated_schedules = []
        conflicts = []
        
        for subject in subjects:
            # Récupérer les enseignants pouvant enseigner cette matière
            teachers = Teacher.objects.filter(subjects=subject, is_available=True)
            
            if not teachers.exists():
                conflicts.append(f"Aucun enseignant disponible pour {subject.name}")
                continue
            
            # Calculer le nombre de séances nécessaires par semaine
            weekly_sessions = self._calculate_weekly_sessions(subject)
            
            sessions_created = 0
            for session in range(weekly_sessions):
                success = False
                exclude_slots = []
                
                for teacher in teachers:
                    # Essayer de trouver un créneau pour cet enseignant
                    for attempt in range(10):  # Maximum 10 tentatives
                        alternative = self.generate_alternative_slot(
                            teacher, subject, week_start, week_end, exclude_slots
                        )
                        
                        if alternative:
                            try:
                                schedule = Schedule.objects.create(
                                    title=f"{subject.name} - {program.name}",
                                    subject=subject,
                                    teacher=teacher,
                                    room=alternative['room'],
                                    program=program,
                                    day_of_week=alternative['day'],
                                    start_time=alternative['start_time'],
                                    end_time=alternative['end_time'],
                                    week_start=week_start,
                                    week_end=week_end,
                                    created_by=created_by
                                )
                                
                                generated_schedules.append(schedule)
                                sessions_created += 1
                                success = True
                                print(f"  ✅ {subject.name} - {self._get_day_name(alternative['day'])} {alternative['start_time']}")
                                break
                                
                            except ValidationError as e:
                                slot_id = f"{alternative['day']}_{alternative['start_time']}_{alternative['end_time']}"
                                exclude_slots.append(slot_id)
                                continue
                    
                    if success:
                        break
                
                if not success:
                    conflicts.append(f"Impossible de programmer {subject.name} (session {session + 1})")
        
        return {
            'generated_schedules': generated_schedules,
            'conflicts': conflicts,
            'program': program.name
        }
    
    def _calculate_weekly_sessions(self, subject):
        """Calcule le nombre de séances par semaine selon les heures de la matière"""
        hours_per_week = subject.hours_per_week
        
        if hours_per_week <= 1.5:
            return 1
        elif hours_per_week <= 3:
            return 2
        elif hours_per_week <= 4.5:
            return 3
        else:
            return min(4, int(hours_per_week / 1.5))
    
    def _get_day_name(self, day_number):
        """Convertit le numéro du jour en nom"""
        days = {1: 'Lundi', 2: 'Mardi', 3: 'Mercredi', 4: 'Jeudi', 5: 'Vendredi'}
        return days.get(day_number, 'Inconnu')
    
    def generate_full_schedule(self, week_start, week_end, created_by):
        """Génère l'emploi du temps complet pour tous les programmes"""
        print("🚀 GÉNÉRATION AUTOMATIQUE DES EMPLOIS DU TEMPS")
        print("=" * 60)
        
        all_results = []
        all_conflicts = []
        total_schedules = 0
        
        programs = Program.objects.all()
        
        for program in programs:
            result = self.generate_schedule_for_program(program, week_start, week_end, created_by)
            all_results.append(result)
            all_conflicts.extend(result['conflicts'])
            total_schedules += len(result['generated_schedules'])
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"• Total programmes: {programs.count()}")
        print(f"• Créneaux générés: {total_schedules}")
        print(f"• Conflits détectés: {len(all_conflicts)}")
        
        if all_conflicts:
            print(f"\n⚠️ CONFLITS:")
            for i, conflict in enumerate(all_conflicts, 1):
                print(f"  {i}. {conflict}")
        
        return {
            'total_schedules': total_schedules,
            'total_conflicts': len(all_conflicts),
            'results_by_program': all_results,
            'conflicts': all_conflicts
        }

def main():
    """Fonction principale pour tester le générateur"""
    from authentication.models import User
    from datetime import date
    
    # Récupérer un utilisateur admin pour créer les emplois du temps
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(role='admin').first()
    
    if not admin_user:
        print("❌ Aucun utilisateur administrateur trouvé")
        return
    
    # Générer pour la semaine du 2 septembre au 20 décembre 2024
    week_start = date(2024, 9, 2)
    week_end = date(2024, 12, 20)
    
    generator = ScheduleGenerator()
    result = generator.generate_full_schedule(week_start, week_end, admin_user)
    
    print(f"\n🎉 Génération terminée!")
    print(f"Consultez l'admin Django pour voir les emplois du temps: http://127.0.0.1:8000/admin/schedule/schedule/")

if __name__ == "__main__":
    main()
