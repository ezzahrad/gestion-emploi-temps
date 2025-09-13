# timetable_solver.py - Solveur OR-Tools pour génération d'emploi du temps
import os
import sys
import django
from datetime import datetime, date, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from ortools.sat.python import cp_model
from django.db import transaction
from django.contrib.auth import get_user_model
from core.models import (
    Department, Program, Room, Subject, Teacher, Student,
    TimeSlot, Schedule, TimetableGeneration
)

User = get_user_model()

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimetableSolver:
    """Solveur d'emploi du temps utilisant OR-Tools CP-SAT"""
    
    def __init__(self, user: User, start_date: date, end_date: date, programs: List[Program] = None):
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.programs = programs or Program.objects.filter(is_active=True)
        
        # Données du problème
        self.subjects = []
        self.teachers = []
        self.rooms = []
        self.time_slots = []
        self.assignments = []  # (subject, teacher, programs, duration_hours)
        
        # Variables du modèle
        self.model = cp_model.CpModel()
        self.schedule_vars = {}  # Variables de planification
        self.assignment_vars = {}  # Variables d'affectation
        
        # Statistiques
        self.stats = {
            'total_assignments': 0,
            'total_sessions_planned': 0,
            'conflicts_resolved': 0,
            'optimization_score': 0
        }
        
        self.generation_log = None
    
    def generate_timetable(self) -> Dict:
        """Méthode principale de génération d'emploi du temps"""
        start_time = datetime.now()
        
        # Créer le log de génération
        self.generation_log = TimetableGeneration.objects.create(
            generated_by=self.user,
            status='pending',
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.generation_log.programs.set(self.programs)
        
        try:
            logger.info("🚀 Début de la génération d'emploi du temps")
            
            # 1. Collecter les données
            self._collect_data()
            
            # 2. Créer le modèle de contraintes
            self._create_constraint_model()
            
            # 3. Résoudre le problème
            solution = self._solve_model()
            
            if not solution:
                raise Exception("Aucune solution trouvée pour ce problème d'emploi du temps")
            
            # 4. Créer les emplois du temps en base
            with transaction.atomic():
                self._create_schedules_from_solution(solution)
            
            # 5. Calculer les statistiques
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_generation_log('success', processing_time)
            
            logger.info("✅ Génération d'emploi du temps terminée avec succès")
            
            return {
                'success': True,
                'message': 'Emploi du temps généré avec succès',
                'stats': self.stats,
                'generation_id': self.generation_log.id
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_generation_log('failed', processing_time, str(e))
            
            return {
                'success': False,
                'error': str(e),
                'generation_id': self.generation_log.id
            }
    
    def _collect_data(self):
        """Collecter toutes les données nécessaires"""
        logger.info("📊 Collecte des données...")
        
        # Récupérer toutes les matières des programmes sélectionnés
        self.subjects = Subject.objects.filter(
            programs__in=self.programs,
            is_active=True
        ).distinct()
        
        # Récupérer tous les enseignants disponibles
        self.teachers = Teacher.objects.filter(
            is_available=True,
            subjects__in=self.subjects
        ).distinct()
        
        # Récupérer toutes les salles disponibles
        self.rooms = Room.objects.filter(is_available=True)
        
        # Récupérer tous les créneaux horaires
        self.time_slots = TimeSlot.objects.filter(is_active=True).order_by('day_of_week', 'start_time')
        
        # Créer les affectations (matière -> enseignant -> programmes)
        self._create_assignments()
        
        logger.info(f"📈 Données collectées:")
        logger.info(f"  • {len(self.subjects)} matières")
        logger.info(f"  • {len(self.teachers)} enseignants")
        logger.info(f"  • {len(self.rooms)} salles")
        logger.info(f"  • {len(self.time_slots)} créneaux")
        logger.info(f"  • {len(self.assignments)} affectations à planifier")
    
    def _create_assignments(self):
        """Créer les affectations matière-enseignant-programmes"""
        self.assignments = []
        assignment_id = 0
        
        for subject in self.subjects:
            # Récupérer les enseignants qui peuvent enseigner cette matière
            subject_teachers = subject.teachers.filter(is_available=True)
            
            if not subject_teachers.exists():
                logger.warning(f"⚠️ Aucun enseignant disponible pour {subject.name}")
                continue
            
            # Récupérer les programmes qui ont cette matière
            subject_programs = subject.programs.filter(id__in=[p.id for p in self.programs])
            
            if not subject_programs.exists():
                continue
            
            for teacher in subject_teachers:
                # Calculer le nombre d'heures nécessaires
                total_hours_needed = subject.hours_per_week
                sessions_needed = max(1, total_hours_needed // 2)  # Sessions de 2h par défaut
                
                assignment = {
                    'id': assignment_id,
                    'subject': subject,
                    'teacher': teacher,
                    'programs': list(subject_programs),
                    'sessions_needed': sessions_needed,
                    'hours_per_session': 2,
                    'total_hours': total_hours_needed
                }
                
                self.assignments.append(assignment)
                assignment_id += 1
        
        self.stats['total_assignments'] = len(self.assignments)
    
    def _create_constraint_model(self):
        """Créer le modèle de contraintes CP-SAT"""
        logger.info("🔧 Création du modèle de contraintes...")
        
        # Variables de décision: schedule[assignment_id, room_id, slot_id, week] = 0 ou 1
        num_weeks = (self.end_date - self.start_date).days // 7 + 1
        
        for assignment in self.assignments:
            for room in self.rooms:
                for time_slot in self.time_slots:
                    for week in range(num_weeks):
                        var_name = f"schedule_{assignment['id']}_{room.id}_{time_slot.id}_{week}"
                        self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)] = \
                            self.model.NewBoolVar(var_name)
        
        # Contrainte 1: Chaque affectation doit avoir le bon nombre de sessions
        for assignment in self.assignments:
            sessions_vars = []
            for room in self.rooms:
                for time_slot in self.time_slots:
                    for week in range(num_weeks):
                        sessions_vars.append(
                            self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)]
                        )
            
            self.model.Add(sum(sessions_vars) == assignment['sessions_needed'])
        
        # Contrainte 2: Pas de conflit d'enseignant
        for teacher in self.teachers:
            teacher_assignments = [a for a in self.assignments if a['teacher'] == teacher]
            
            for time_slot in self.time_slots:
                for week in range(num_weeks):
                    teacher_vars = []
                    for assignment in teacher_assignments:
                        for room in self.rooms:
                            teacher_vars.append(
                                self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)]
                            )
                    
                    # Un enseignant ne peut être que dans une salle à la fois
                    if teacher_vars:
                        self.model.Add(sum(teacher_vars) <= 1)
        
        # Contrainte 3: Pas de conflit de salle
        for room in self.rooms:
            for time_slot in self.time_slots:
                for week in range(num_weeks):
                    room_vars = []
                    for assignment in self.assignments:
                        room_vars.append(
                            self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)]
                        )
                    
                    # Une salle ne peut avoir qu'un cours à la fois
                    self.model.Add(sum(room_vars) <= 1)
        
        # Contrainte 4: Capacité des salles
        for assignment in self.assignments:
            total_students = sum([
                program.students.filter(is_active=True).count() 
                for program in assignment['programs']
            ])
            
            for room in self.rooms:
                if total_students > room.capacity:
                    # Interdire cette combinaison
                    for time_slot in self.time_slots:
                        for week in range(num_weeks):
                            self.model.Add(
                                self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)] == 0
                            )
        
        # Contrainte 5: Respect des disponibilités des enseignants
        for assignment in self.assignments:
            teacher = assignment['teacher']
            unavailable_slots = teacher.unavailable_slots_list
            
            for unavailable_slot in unavailable_slots:
                day = unavailable_slot.get('day', 0)
                start_time = unavailable_slot.get('start_time', '00:00')
                
                # Trouver les créneaux correspondants
                conflicting_slots = self.time_slots.filter(
                    day_of_week=day,
                    start_time__lte=start_time
                )
                
                for slot in conflicting_slots:
                    for room in self.rooms:
                        for week in range(num_weeks):
                            self.model.Add(
                                self.schedule_vars[(assignment['id'], room.id, slot.id, week)] == 0
                            )
        
        # Contrainte 6: Limites horaires des enseignants
        for teacher in self.teachers:
            teacher_assignments = [a for a in self.assignments if a['teacher'] == teacher]
            
            for week in range(num_weeks):
                weekly_hours = []
                for assignment in teacher_assignments:
                    for room in self.rooms:
                        for time_slot in self.time_slots:
                            weekly_hours.append(
                                self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)] *
                                assignment['hours_per_session']
                            )
                
                if weekly_hours:
                    self.model.Add(sum(weekly_hours) <= teacher.max_hours_per_week)
        
        # Objectif: Maximiser l'utilisation équilibrée des créneaux
        objective_vars = []
        
        # Favoriser les créneaux de haute priorité
        for assignment in self.assignments:
            for room in self.rooms:
                for time_slot in self.time_slots:
                    for week in range(num_weeks):
                        # Pondérer par la priorité du créneau et de la salle
                        weight = time_slot.priority * room.priority
                        objective_vars.append(
                            self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)] * weight
                        )
        
        self.model.Maximize(sum(objective_vars))
        
        logger.info("✅ Modèle de contraintes créé")
    
    def _solve_model(self) -> Optional[cp_model.CpSolver]:
        """Résoudre le modèle"""
        logger.info("🧮 Résolution du problème...")
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300  # 5 minutes max
        solver.parameters.num_search_workers = 4      # Parallélisation
        
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL:
            logger.info("🎯 Solution optimale trouvée")
            self.stats['optimization_score'] = 100
        elif status == cp_model.FEASIBLE:
            logger.info("✅ Solution réalisable trouvée")
            self.stats['optimization_score'] = 80
        else:
            logger.error("❌ Aucune solution trouvée")
            return None
        
        logger.info(f"📊 Statistiques du solveur:")
        logger.info(f"  • Temps de résolution: {solver.WallTime():.2f}s")
        logger.info(f"  • Branches explorées: {solver.NumBranches()}")
        logger.info(f"  • Conflits: {solver.NumConflicts()}")
        
        return solver
    
    def _create_schedules_from_solution(self, solver: cp_model.CpSolver):
        """Créer les emplois du temps en base à partir de la solution"""
        logger.info("💾 Création des emplois du temps...")
        
        # Supprimer les anciens emplois du temps pour cette période
        Schedule.objects.filter(
            start_date__gte=self.start_date,
            end_date__lte=self.end_date,
            programs__in=self.programs
        ).delete()
        
        num_weeks = (self.end_date - self.start_date).days // 7 + 1
        schedules_created = 0
        
        for assignment in self.assignments:
            for room in self.rooms:
                for time_slot in self.time_slots:
                    for week in range(num_weeks):
                        var = self.schedule_vars[(assignment['id'], room.id, time_slot.id, week)]
                        
                        if solver.Value(var) == 1:
                            # Calculer la date de cette semaine
                            week_start = self.start_date + timedelta(weeks=week)
                            session_date = week_start + timedelta(days=time_slot.day_of_week)
                            
                            # Créer l'emploi du temps
                            schedule = Schedule.objects.create(
                                title=f"{assignment['subject'].name} - {assignment['teacher'].user.get_full_name()}",
                                subject=assignment['subject'],
                                teacher=assignment['teacher'],
                                room=room,
                                time_slot=time_slot,
                                start_date=session_date,
                                end_date=session_date,
                                duration_minutes=assignment['hours_per_session'] * 60,
                                created_by=self.user
                            )
                            
                            # Associer aux programmes
                            schedule.programs.set(assignment['programs'])
                            
                            schedules_created += 1
                            
                            logger.debug(f"📅 Créé: {schedule.title} - {session_date} {time_slot}")
        
        self.stats['total_sessions_planned'] = schedules_created
        logger.info(f"✅ {schedules_created} séances créées")
    
    def _update_generation_log(self, status: str, processing_time: float, error_message: str = None):
        """Mettre à jour le log de génération"""
        self.generation_log.status = status
        self.generation_log.processing_time = processing_time
        self.generation_log.total_sessions_planned = self.stats['total_sessions_planned']
        self.generation_log.conflicts_resolved = self.stats['conflicts_resolved']
        self.generation_log.optimization_score = self.stats['optimization_score']
        
        if error_message:
            self.generation_log.execution_log = error_message
        else:
            self.generation_log.execution_log = json.dumps(self.stats, indent=2)
        
        self.generation_log.save()


# Fonctions utilitaires

def generate_timetable_for_programs(
    user_id: int, 
    start_date: date, 
    end_date: date, 
    program_ids: List[int] = None
) -> Dict:
    """Générer un emploi du temps pour des programmes spécifiques"""
    try:
        user = User.objects.get(id=user_id)
        
        if program_ids:
            programs = Program.objects.filter(id__in=program_ids, is_active=True)
        else:
            programs = Program.objects.filter(is_active=True)
        
        if not programs.exists():
            return {'success': False, 'error': 'Aucun programme valide trouvé'}
        
        solver = TimetableSolver(user, start_date, end_date, list(programs))
        return solver.generate_timetable()
        
    except User.DoesNotExist:
        return {'success': False, 'error': 'Utilisateur introuvable'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def quick_timetable_generation(user_id: int) -> Dict:
    """Génération rapide d'emploi du temps pour le semestre actuel"""
    today = date.today()
    
    # Déterminer les dates du semestre
    if 2 <= today.month <= 6:  # Semestre de printemps
        start_date = date(today.year, 2, 1)
        end_date = date(today.year, 6, 30)
    else:  # Semestre d'automne
        if today.month >= 9:
            start_date = date(today.year, 9, 1)
            end_date = date(today.year + 1, 1, 31)
        else:
            start_date = date(today.year - 1, 9, 1)
            end_date = date(today.year, 1, 31)
    
    return generate_timetable_for_programs(user_id, start_date, end_date)


# Script principal
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Générer un emploi du temps avec OR-Tools')
    parser.add_argument('--user-id', type=int, required=True, help='ID de l\'utilisateur')
    parser.add_argument('--start-date', type=str, help='Date de début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Date de fin (YYYY-MM-DD)')
    parser.add_argument('--programs', nargs='+', type=int, help='IDs des programmes')
    
    args = parser.parse_args()
    
    if args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        result = generate_timetable_for_programs(args.user_id, start_date, end_date, args.programs)
    else:
        result = quick_timetable_generation(args.user_id)
    
    if result['success']:
        print("✅ Génération réussie !")
        print(f"📊 Statistiques: {result['stats']}")
    else:
        print(f"❌ Erreur: {result['error']}")
        sys.exit(1)
