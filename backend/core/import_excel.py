# import_excel.py - Script d'importation Excel pour AppGET
import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, time, date, timedelta
import logging
import traceback
import re
from typing import Dict, List, Tuple, Optional
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from core.models import (
    Department, Program, Room, Subject, Teacher, Student,
    TimeSlot, Schedule, ExcelImportLog
)

User = get_user_model()

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('excel_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ExcelImporter:
    """Classe pour importer les données Excel dans la base de données"""
    
    def __init__(self, file_path: str, imported_by_user: User):
        self.file_path = file_path
        self.imported_by = imported_by_user
        self.import_log = None
        self.errors = []
        self.success_messages = []
        self.stats = {
            'departments': 0,
            'programs': 0,
            'rooms': 0,
            'subjects': 0,
            'teachers': 0,
            'students': 0,
            'time_slots': 0,
            'schedules': 0
        }
        
    def import_data(self) -> Dict:
        """Méthode principale d'importation"""
        start_time = datetime.now()
        
        # Créer le log d'importation
        self.import_log = ExcelImportLog.objects.create(
            filename=os.path.basename(self.file_path),
            imported_by=self.imported_by,
            status='pending'
        )
        
        try:
            logger.info(f"Début de l'importation du fichier: {self.file_path}")
            
            # Lire le fichier Excel
            excel_data = self._read_excel_file()
            if not excel_data:
                raise Exception("Impossible de lire le fichier Excel")
            
            # Traitement des données
            with transaction.atomic():
                self._process_excel_data(excel_data)
            
            # Succès
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_import_log('success', processing_time)
            
            return {
                'success': True,
                'message': 'Importation réussie',
                'stats': self.stats,
                'log_id': self.import_log.id
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'importation: {str(e)}")
            logger.error(traceback.format_exc())
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_import_log('failed', processing_time, str(e))
            
            return {
                'success': False,
                'error': str(e),
                'log_id': self.import_log.id
            }
    
    def _read_excel_file(self) -> Dict:
        """Lire le fichier Excel et retourner les données"""
        try:
            # Lire toutes les feuilles
            excel_data = pd.read_excel(
                self.file_path,
                sheet_name=None,  # Lit toutes les feuilles
                header=0,
                na_values=['', 'N/A', 'n/a', 'NULL', 'null', '#N/A']
            )
            
            logger.info(f"Feuilles trouvées: {list(excel_data.keys())}")
            
            # Nettoyer les données
            for sheet_name, df in excel_data.items():
                # Supprimer les lignes vides
                df.dropna(how='all', inplace=True)
                
                # Nettoyer les noms des colonnes
                df.columns = df.columns.str.strip()
                
                excel_data[sheet_name] = df
                logger.info(f"Feuille '{sheet_name}': {len(df)} lignes")
            
            return excel_data
            
        except Exception as e:
            logger.error(f"Erreur lecture Excel: {str(e)}")
            raise
    
    def _process_excel_data(self, excel_data: Dict):
        """Traiter les données Excel selon la structure détectée"""
        
        # Détecter la structure et traiter en conséquence
        for sheet_name, df in excel_data.items():
            logger.info(f"Traitement de la feuille: {sheet_name}")
            
            # Analyser la structure de la feuille
            sheet_type = self._detect_sheet_type(sheet_name, df)
            
            if sheet_type == 'planning':
                self._process_planning_sheet(df, sheet_name)
            elif sheet_type == 'teachers':
                self._process_teachers_sheet(df)
            elif sheet_type == 'students':
                self._process_students_sheet(df)
            elif sheet_type == 'rooms':
                self._process_rooms_sheet(df)
            elif sheet_type == 'subjects':
                self._process_subjects_sheet(df)
            else:
                # Essayer de traiter comme un planning générique
                self._process_generic_planning_sheet(df, sheet_name)
    
    def _detect_sheet_type(self, sheet_name: str, df: pd.DataFrame) -> str:
        """Détecter le type de feuille Excel"""
        sheet_name_lower = sheet_name.lower()
        columns_lower = [col.lower() for col in df.columns]
        
        # Patterns pour identifier le type de feuille
        if any(word in sheet_name_lower for word in ['planning', 'emploi', 'timetable', 'schedule']):
            return 'planning'
        elif any(word in sheet_name_lower for word in ['enseignant', 'teacher', 'prof']):
            return 'teachers'
        elif any(word in sheet_name_lower for word in ['etudiant', 'student', 'eleve']):
            return 'students'
        elif any(word in sheet_name_lower for word in ['salle', 'room', 'amphi']):
            return 'rooms'
        elif any(word in sheet_name_lower for word in ['matiere', 'subject', 'cours']):
            return 'subjects'
        
        # Analyser les colonnes pour détecter automatiquement
        if any(col in columns_lower for col in ['heure', 'time', 'horaire', 'creneau']):
            return 'planning'
        
        return 'unknown'
    
    def _process_planning_sheet(self, df: pd.DataFrame, sheet_name: str):
        """Traiter une feuille de planning"""
        logger.info(f"Traitement du planning: {sheet_name}")
        
        # Colonnes attendues (variations possibles)
        column_mappings = {
            # Matière/Cours
            'subject': ['matiere', 'matière', 'cours', 'subject', 'discipline'],
            'subject_code': ['code_matiere', 'code_cours', 'code', 'subject_code'],
            
            # Enseignant
            'teacher': ['enseignant', 'professeur', 'prof', 'teacher', 'instructor'],
            
            # Programme/Filière
            'program': ['filiere', 'filière', 'program', 'programme', 'niveau', 'classe'],
            
            # Salle
            'room': ['salle', 'room', 'local', 'lieu'],
            
            # Horaire
            'day': ['jour', 'day', 'journee'],
            'start_time': ['heure_debut', 'debut', 'start_time', 'heure'],
            'end_time': ['heure_fin', 'fin', 'end_time'],
            'duration': ['duree', 'durée', 'duration'],
            
            # Dates
            'start_date': ['date_debut', 'date_start', 'debut_periode'],
            'end_date': ['date_fin', 'date_end', 'fin_periode'],
            
            # Autres
            'type': ['type', 'type_cours', 'cours_type'],
            'notes': ['notes', 'remarques', 'observation']
        }
        
        # Mapper les colonnes
        mapped_columns = self._map_columns(df.columns, column_mappings)
        
        # Traitement ligne par ligne
        for index, row in df.iterrows():
            try:
                self._process_planning_row(row, mapped_columns, sheet_name)
                self.stats['schedules'] += 1
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _process_planning_row(self, row: pd.Series, mapped_columns: Dict, sheet_name: str):
        """Traiter une ligne de planning"""
        
        # Extraction des données
        subject_name = self._get_cell_value(row, mapped_columns.get('subject'))
        subject_code = self._get_cell_value(row, mapped_columns.get('subject_code'))
        teacher_name = self._get_cell_value(row, mapped_columns.get('teacher'))
        program_name = self._get_cell_value(row, mapped_columns.get('program'))
        room_name = self._get_cell_value(row, mapped_columns.get('room'))
        day_str = self._get_cell_value(row, mapped_columns.get('day'))
        start_time_str = self._get_cell_value(row, mapped_columns.get('start_time'))
        end_time_str = self._get_cell_value(row, mapped_columns.get('end_time'))
        
        # Validation des données obligatoires
        if not all([subject_name, teacher_name, room_name]):
            raise ValueError("Données obligatoires manquantes (matière, enseignant, salle)")
        
        # Créer ou récupérer les objets
        department = self._get_or_create_department("Département Général")
        subject = self._get_or_create_subject(subject_name, subject_code, department)
        teacher = self._get_or_create_teacher(teacher_name, department)
        room = self._get_or_create_room(room_name, department)
        program = self._get_or_create_program(program_name, department) if program_name else None
        
        # Traitement des horaires
        time_slot = self._get_or_create_time_slot(day_str, start_time_str, end_time_str)
        
        # Dates par défaut (semestre actuel)
        start_date, end_date = self._get_semester_dates()
        
        # Créer l'emploi du temps
        schedule_title = f"{subject.name} - {program.name if program else 'Cours'}"
        
        # Vérifier si l'emploi du temps existe déjà
        existing_schedule = Schedule.objects.filter(
            subject=subject,
            teacher=teacher,
            room=room,
            time_slot=time_slot,
            start_date=start_date
        ).first()
        
        if not existing_schedule:
            schedule = Schedule.objects.create(
                title=schedule_title,
                subject=subject,
                teacher=teacher,
                room=room,
                time_slot=time_slot,
                start_date=start_date,
                end_date=end_date,
                created_by=self.imported_by
            )
            
            if program:
                schedule.programs.add(program)
            
            logger.info(f"Emploi du temps créé: {schedule_title}")
        else:
            logger.info(f"Emploi du temps existant: {schedule_title}")
    
    def _map_columns(self, df_columns: List[str], mappings: Dict) -> Dict:
        """Mapper les colonnes du DataFrame avec les noms attendus"""
        mapped = {}
        df_columns_lower = [col.lower().strip() for col in df_columns]
        
        for field, possible_names in mappings.items():
            for possible_name in possible_names:
                if possible_name in df_columns_lower:
                    original_index = df_columns_lower.index(possible_name)
                    mapped[field] = df_columns[original_index]
                    break
        
        logger.info(f"Colonnes mappées: {mapped}")
        return mapped
    
    def _get_cell_value(self, row: pd.Series, column_name: str) -> Optional[str]:
        """Récupérer la valeur d'une cellule en gérant les valeurs nulles"""
        if not column_name or column_name not in row:
            return None
        
        value = row[column_name]
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        
        return str(value).strip()
    
    def _get_or_create_department(self, name: str) -> Department:
        """Créer ou récupérer un département"""
        department, created = Department.objects.get_or_create(
            name=name,
            defaults={
                'code': self._generate_department_code(name),
                'description': f'Département {name}'
            }
        )
        if created:
            self.stats['departments'] += 1
            logger.info(f"Département créé: {name}")
        
        return department
    
    def _get_or_create_subject(self, name: str, code: Optional[str], department: Department) -> Subject:
        """Créer ou récupérer une matière"""
        if not code:
            code = self._generate_subject_code(name)
        
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'department': department,
                'subject_type': 'lecture',
                'credits': 3,
                'hours_per_week': 3,
                'semester': 1
            }
        )
        if created:
            self.stats['subjects'] += 1
            logger.info(f"Matière créée: {name} ({code})")
        
        return subject
    
    def _get_or_create_teacher(self, full_name: str, department: Department) -> Teacher:
        """Créer ou récupérer un enseignant"""
        # Analyser le nom complet
        name_parts = full_name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        else:
            first_name = full_name
            last_name = ''
        
        # Chercher ou créer l'utilisateur
        username = self._generate_username(first_name, last_name)
        email = f"{username}@university.edu"
        
        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'teacher'
            }
        )
        
        # Chercher ou créer l'enseignant
        teacher, teacher_created = Teacher.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': self._generate_employee_id(),
                'specialization': department.name,
                'teacher_type': 'lecturer'
            }
        )
        
        if teacher_created:
            teacher.departments.add(department)
            self.stats['teachers'] += 1
            logger.info(f"Enseignant créé: {full_name}")
        
        return teacher
    
    def _get_or_create_room(self, name: str, department: Department) -> Room:
        """Créer ou récupérer une salle"""
        # Détecter le type de salle
        name_lower = name.lower()
        if 'amphi' in name_lower or 'amphitheatre' in name_lower:
            room_type = 'amphitheater'
            capacity = 200
        elif 'td' in name_lower:
            room_type = 'td'
            capacity = 30
        elif 'tp' in name_lower or 'lab' in name_lower:
            room_type = 'lab'
            capacity = 25
        else:
            room_type = 'lecture'
            capacity = 50
        
        room, created = Room.objects.get_or_create(
            name=name,
            defaults={
                'code': self._generate_room_code(name),
                'room_type': room_type,
                'capacity': capacity,
                'department': department
            }
        )
        if created:
            self.stats['rooms'] += 1
            logger.info(f"Salle créée: {name}")
        
        return room
    
    def _get_or_create_program(self, name: str, department: Department) -> Program:
        """Créer ou récupérer un programme"""
        # Détecter le niveau
        name_lower = name.lower()
        if 'l1' in name_lower or 'licence 1' in name_lower:
            level = 'L1'
        elif 'l2' in name_lower or 'licence 2' in name_lower:
            level = 'L2'
        elif 'l3' in name_lower or 'licence 3' in name_lower:
            level = 'L3'
        elif 'm1' in name_lower or 'master 1' in name_lower:
            level = 'M1'
        elif 'm2' in name_lower or 'master 2' in name_lower:
            level = 'M2'
        else:
            level = 'L1'  # Par défaut
        
        program, created = Program.objects.get_or_create(
            name=name,
            department=department,
            level=level,
            defaults={
                'code': self._generate_program_code(name, level),
                'capacity': 30
            }
        )
        if created:
            self.stats['programs'] += 1
            logger.info(f"Programme créé: {name} ({level})")
        
        return program
    
    def _get_or_create_time_slot(self, day_str: str, start_time_str: str, end_time_str: str) -> TimeSlot:
        """Créer ou récupérer un créneau horaire"""
        # Mapper les jours
        day_mapping = {
            'lundi': 0, 'monday': 0, 'lun': 0, 'mon': 0,
            'mardi': 1, 'tuesday': 1, 'mar': 1, 'tue': 1,
            'mercredi': 2, 'wednesday': 2, 'mer': 2, 'wed': 2,
            'jeudi': 3, 'thursday': 3, 'jeu': 3, 'thu': 3,
            'vendredi': 4, 'friday': 4, 'ven': 4, 'fri': 4,
            'samedi': 5, 'saturday': 5, 'sam': 5, 'sat': 5
        }
        
        day_of_week = day_mapping.get(day_str.lower().strip(), 0) if day_str else 0
        
        # Parser les heures
        start_time = self._parse_time(start_time_str) if start_time_str else time(8, 0)
        end_time = self._parse_time(end_time_str) if end_time_str else time(start_time.hour + 2, start_time.minute)
        
        # Nom du créneau
        slot_name = f"{day_str or 'Lundi'} {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        
        time_slot, created = TimeSlot.objects.get_or_create(
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            defaults={
                'name': slot_name,
                'is_active': True
            }
        )
        if created:
            self.stats['time_slots'] += 1
            logger.info(f"Créneau créé: {slot_name}")
        
        return time_slot
    
    def _parse_time(self, time_str: str) -> time:
        """Parser une chaîne d'heure en objet time"""
        if not time_str:
            return time(8, 0)
        
        time_str = str(time_str).strip()
        
        # Patterns possibles
        patterns = [
            r'(\d{1,2}):(\d{2})',      # 08:30, 14:15
            r'(\d{1,2})h(\d{2})',      # 8h30, 14h15
            r'(\d{1,2})h',             # 8h, 14h
            r'(\d{1,2})',              # 8, 14
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                
                # Validation
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return time(hour, minute)
        
        # Par défaut
        logger.warning(f"Impossible de parser l'heure: {time_str}, utilisation de 08:00")
        return time(8, 0)
    
    def _get_semester_dates(self) -> Tuple[date, date]:
        """Obtenir les dates de début et fin du semestre actuel"""
        today = date.today()
        year = today.year
        
        # Semestre de printemps (février - juin)
        if 2 <= today.month <= 6:
            start_date = date(year, 2, 1)
            end_date = date(year, 6, 30)
        # Semestre d'automne (septembre - janvier)
        else:
            if today.month >= 9:
                start_date = date(year, 9, 1)
                end_date = date(year + 1, 1, 31)
            else:
                start_date = date(year - 1, 9, 1)
                end_date = date(year, 1, 31)
        
        return start_date, end_date
    
    # Méthodes utilitaires pour générer les codes
    def _generate_department_code(self, name: str) -> str:
        """Générer un code département"""
        code = re.sub(r'[^A-Za-z0-9]', '', name)[:10].upper()
        return code if code else 'DEPT'
    
    def _generate_subject_code(self, name: str) -> str:
        """Générer un code matière"""
        words = name.split()
        code = ''.join([word[0].upper() for word in words if word])[:10]
        return code + str(hash(name) % 1000) if len(code) < 3 else code
    
    def _generate_room_code(self, name: str) -> str:
        """Générer un code salle"""
        return re.sub(r'[^A-Za-z0-9]', '', name)[:20].upper()
    
    def _generate_program_code(self, name: str, level: str) -> str:
        """Générer un code programme"""
        name_code = re.sub(r'[^A-Za-z0-9]', '', name)[:8].upper()
        return f"{name_code}_{level}"
    
    def _generate_username(self, first_name: str, last_name: str) -> str:
        """Générer un nom d'utilisateur"""
        username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '.')
        return re.sub(r'[^a-z0-9.]', '', username)[:30]
    
    def _generate_employee_id(self) -> str:
        """Générer un ID employé"""
        import random
        return f"EMP{random.randint(10000, 99999)}"
    
    def _process_generic_planning_sheet(self, df: pd.DataFrame, sheet_name: str):
        """Traiter une feuille de planning générique"""
        logger.info(f"Traitement générique de: {sheet_name}")
        
        # Essayer de détecter automatiquement les colonnes importantes
        columns = df.columns.tolist()
        logger.info(f"Colonnes disponibles: {columns}")
        
        # Pour chaque ligne, essayer d'extraire les informations
        for index, row in df.iterrows():
            try:
                # Chercher les cellules non vides
                non_empty_values = []
                for col in columns:
                    value = self._get_cell_value(row, col)
                    if value:
                        non_empty_values.append(value)
                
                if len(non_empty_values) >= 3:  # Au minimum matière, enseignant, salle
                    # Essayer de créer un planning basique
                    self._create_basic_schedule_from_values(non_empty_values, sheet_name)
                    self.stats['schedules'] += 1
                    
            except Exception as e:
                error_msg = f"Erreur ligne {index + 2} (feuille {sheet_name}): {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    def _create_basic_schedule_from_values(self, values: List[str], sheet_name: str):
        """Créer un planning basique à partir des valeurs"""
        # Supposer que les 3 premières valeurs sont: matière, enseignant, salle
        subject_name = values[0]
        teacher_name = values[1] if len(values) > 1 else "Enseignant Inconnu"
        room_name = values[2] if len(values) > 2 else "Salle Inconnue"
        
        department = self._get_or_create_department("Import " + sheet_name)
        subject = self._get_or_create_subject(subject_name, None, department)
        teacher = self._get_or_create_teacher(teacher_name, department)
        room = self._get_or_create_room(room_name, department)
        time_slot = self._get_or_create_time_slot("Lundi", "08:00", "10:00")
        
        start_date, end_date = self._get_semester_dates()
        
        # Créer l'emploi du temps
        Schedule.objects.get_or_create(
            subject=subject,
            teacher=teacher,
            room=room,
            time_slot=time_slot,
            start_date=start_date,
            defaults={
                'title': f"{subject.name} - Import {sheet_name}",
                'end_date': end_date,
                'created_by': self.imported_by
            }
        )
    
    def _update_import_log(self, status: str, processing_time: float, error_message: str = None):
        """Mettre à jour le log d'importation"""
        self.import_log.status = status
        self.import_log.processing_time = processing_time
        self.import_log.total_rows = sum(self.stats.values())
        self.import_log.successful_rows = self.stats['schedules']
        self.import_log.failed_rows = len(self.errors)
        
        if error_message:
            self.import_log.error_log = error_message
        
        self.import_log.success_log = json.dumps(self.stats, indent=2)
        self.import_log.save()


# Fonction utilitaire pour utilisation externe
def import_excel_file(file_path: str, user_id: int) -> Dict:
    """Fonction utilitaire pour importer un fichier Excel"""
    try:
        user = User.objects.get(id=user_id)
        importer = ExcelImporter(file_path, user)
        return importer.import_data()
    except User.DoesNotExist:
        return {'success': False, 'error': 'Utilisateur introuvable'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Script principal pour exécution en ligne de commande
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Importer un fichier Excel dans AppGET')
    parser.add_argument('file_path', help='Chemin vers le fichier Excel')
    parser.add_argument('--user-id', type=int, default=1, help='ID de l\'utilisateur importateur')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Erreur: Le fichier {args.file_path} n'existe pas")
        sys.exit(1)
    
    print(f"Importation du fichier: {args.file_path}")
    result = import_excel_file(args.file_path, args.user_id)
    
    if result['success']:
        print("✅ Importation réussie !")
        print(f"📊 Statistiques: {result['stats']}")
    else:
        print(f"❌ Erreur: {result['error']}")
        sys.exit(1)
