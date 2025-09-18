"""
Analyseur et importateur pour les fichiers Excel d'emploi du temps
Spécialement conçu pour "Planning amphis_Printemps_24-25.xlsx"
"""
import os
import django
import pandas as pd
import numpy as np
from datetime import datetime, time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

from core.models import Department, Program, Room, Subject, Teacher
from schedule.models import Schedule
from authentication.models import User

def analyze_excel_file(file_path):
    """Analyser la structure du fichier Excel"""
    print("📊 ANALYSE DU FICHIER EXCEL")
    print("=" * 30)
    
    try:
        # Lire toutes les feuilles
        excel_file = pd.ExcelFile(file_path)
        print(f"📄 Fichier: {file_path}")
        print(f"📋 Feuilles trouvées: {excel_file.sheet_names}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📊 Analyse de la feuille: '{sheet_name}'")
            print("-" * 40)
            
            # Lire la feuille
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"📏 Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes")
            print(f"📋 Colonnes: {list(df.columns)}")
            
            # Afficher les premières lignes
            print(f"\n📖 Aperçu des données (5 premières lignes):")
            print(df.head().to_string())
            
            # Analyser les données
            print(f"\n🔍 Analyse des données:")
            for col in df.columns:
                non_null_count = df[col].notna().sum()
                unique_values = df[col].nunique()
                print(f"  {col}: {non_null_count}/{len(df)} valeurs, {unique_values} uniques")
                
                # Afficher quelques exemples de valeurs
                sample_values = df[col].dropna().unique()[:5]
                print(f"    Exemples: {list(sample_values)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return False

def detect_schedule_format(df):
    """Détecter le format du fichier d'emploi du temps"""
    print("\n🔍 DÉTECTION DU FORMAT")
    print("=" * 23)
    
    columns = [col.lower().strip() for col in df.columns]
    print(f"📋 Colonnes détectées: {columns}")
    
    # Formats possibles
    formats = {
        'format_standard': ['titre', 'matiere', 'enseignant', 'salle', 'jour', 'heure_debut', 'heure_fin'],
        'format_planning': ['cours', 'prof', 'amphi', 'jour_semaine', 'horaire'],
        'format_universitaire': ['module', 'enseignant', 'salle', 'créneau', 'date'],
        'format_libre': []  # Format détecté automatiquement
    }
    
    # Tenter de détecter le format
    for format_name, required_cols in formats.items():
        if format_name == 'format_libre':
            continue
            
        matches = sum(1 for col in required_cols if any(col in column for column in columns))
        print(f"📊 {format_name}: {matches}/{len(required_cols)} colonnes trouvées")
        
        if matches >= len(required_cols) * 0.6:  # 60% de correspondance
            print(f"✅ Format détecté: {format_name}")
            return format_name
    
    print("🔧 Format libre détecté - analyse automatique nécessaire")
    return 'format_libre'

def create_mapping_suggestions(df):
    """Créer des suggestions de mapping pour les colonnes"""
    print("\n🗺️  SUGGESTIONS DE MAPPING")
    print("=" * 26)
    
    columns = df.columns.tolist()
    
    # Dictionnaire de mots-clés pour chaque type de champ
    field_keywords = {
        'titre': ['titre', 'cours', 'module', 'matiere', 'subject', 'intitule'],
        'enseignant': ['enseignant', 'prof', 'professeur', 'teacher', 'formateur'],
        'salle': ['salle', 'local', 'amphi', 'amphitheatre', 'room', 'classe'],
        'programme': ['programme', 'filiere', 'niveau', 'promo', 'classe', 'group'],
        'jour': ['jour', 'day', 'journee', 'date'],
        'heure_debut': ['debut', 'start', 'heure_debut', 'h_debut', 'from'],
        'heure_fin': ['fin', 'end', 'heure_fin', 'h_fin', 'to', 'jusqu'],
        'horaire': ['horaire', 'creneau', 'time', 'heures']
    }
    
    suggestions = {}
    
    for field, keywords in field_keywords.items():
        best_match = None
        best_score = 0
        
        for col in columns:
            col_lower = col.lower().strip()
            score = sum(1 for keyword in keywords if keyword in col_lower)
            
            if score > best_score:
                best_score = score
                best_match = col
        
        if best_match:
            suggestions[field] = best_match
            print(f"📌 {field}: {best_match} (score: {best_score})")
        else:
            print(f"❓ {field}: Aucune correspondance trouvée")
    
    return suggestions

def import_from_custom_format(file_path, mapping=None):
    """Importer depuis un format personnalisé"""
    print("\n📥 IMPORT DEPUIS FORMAT PERSONNALISÉ")
    print("=" * 36)
    
    try:
        # Lire le fichier
        df = pd.read_excel(file_path, sheet_name=0)  # Première feuille
        print(f"📊 Lecture de {len(df)} lignes")
        
        # Utiliser le mapping fourni ou détecter automatiquement
        if not mapping:
            mapping = create_mapping_suggestions(df)
        
        print(f"🗺️  Mapping utilisé: {mapping}")
        
        # Compter les imports réussis
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extraire les données selon le mapping
                title = str(row.get(mapping.get('titre', ''), f'Cours {index + 1}')).strip()
                
                # Gérer les enseignants
                teacher_name = str(row.get(mapping.get('enseignant', ''), '')).strip()
                if not teacher_name:
                    errors.append(f"Ligne {index + 2}: Nom d'enseignant manquant")
                    continue
                
                # Gérer les salles
                room_name = str(row.get(mapping.get('salle', ''), '')).strip()
                if not room_name:
                    errors.append(f"Ligne {index + 2}: Nom de salle manquant")
                    continue
                
                # Créer ou récupérer les objets nécessaires
                try:
                    # Créer un département par défaut si nécessaire
                    default_dept, _ = Department.objects.get_or_create(
                        code='IMPORT',
                        defaults={'name': 'Département Importé', 'description': 'Créé lors de l\'import Excel'}
                    )
                    
                    # Créer un programme par défaut
                    default_program, _ = Program.objects.get_or_create(
                        code='IMPORT-PROG',
                        defaults={
                            'name': 'Programme Importé',
                            'department': default_dept,
                            'level': 'L1',
                            'capacity': 30
                        }
                    )
                    
                    # Créer ou récupérer la matière
                    subject, _ = Subject.objects.get_or_create(
                        name=title,
                        defaults={
                            'code': f'SUBJ-{index}',
                            'department': default_dept,
                            'hours_per_week': 2,
                            'coefficient': 1.0
                        }
                    )
                    
                    # Créer ou récupérer l'enseignant
                    teacher_user, created = User.objects.get_or_create(
                        email=f"{teacher_name.lower().replace(' ', '.')}@university.edu",
                        defaults={
                            'username': teacher_name.lower().replace(' ', '_'),
                            'first_name': teacher_name.split()[0] if teacher_name.split() else teacher_name,
                            'last_name': ' '.join(teacher_name.split()[1:]) if len(teacher_name.split()) > 1 else '',
                            'role': 'teacher',
                            'is_active': True
                        }
                    )
                    
                    if created:
                        teacher_user.set_password('teacher123')
                        teacher_user.save()
                    
                    teacher, _ = Teacher.objects.get_or_create(
                        user=teacher_user,
                        defaults={
                            'department': default_dept,
                            'specialization': 'Générale'
                        }
                    )
                    
                    # Créer ou récupérer la salle
                    room, _ = Room.objects.get_or_create(
                        name=room_name,
                        defaults={
                            'department': default_dept,
                            'room_type': 'classroom',
                            'capacity': 50,
                            'is_available': True,
                            'equipment': 'Projecteur, Tableau'
                        }
                    )
                    
                    # Horaires par défaut (à adapter selon votre fichier)
                    start_time = time(9, 0)  # 9h00
                    end_time = time(11, 0)   # 11h00
                    day_of_week = 1  # Mardi
                    
                    # Dates par défaut (semestre en cours)
                    from django.utils import timezone
                    today = timezone.now().date()
                    week_start = today
                    week_end = today + timezone.timedelta(days=90)  # 3 mois
                    
                    # Créer l'emploi du temps
                    schedule, created = Schedule.objects.get_or_create(
                        title=title,
                        subject=subject,
                        teacher=teacher,
                        room=room,
                        program=default_program,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'week_start': week_start,
                            'week_end': week_end,
                            'is_active': True,
                            'notes': f'Importé depuis Excel - ligne {index + 2}'
                        }
                    )
                    
                    if created:
                        imported_count += 1
                        print(f"✅ Ligne {index + 2}: {title} - {teacher_name} - {room_name}")
                    else:
                        print(f"⚠️  Ligne {index + 2}: Déjà existant - {title}")
                
                except Exception as e:
                    errors.append(f"Ligne {index + 2}: Erreur lors de la création - {str(e)}")
                    continue
                
            except Exception as e:
                errors.append(f"Ligne {index + 2}: Erreur de traitement - {str(e)}")
                continue
        
        print(f"\n📊 RÉSULTATS D'IMPORT:")
        print(f"✅ Cours importés: {imported_count}")
        print(f"❌ Erreurs: {len(errors)}")
        
        if errors:
            print(f"\n📋 Premières erreurs:")
            for error in errors[:10]:
                print(f"  • {error}")
        
        return imported_count > 0
        
    except Exception as e:
        print(f"❌ Erreur fatale lors de l'import: {e}")
        return False

def main():
    """Fonction principale"""
    print("📚 ANALYSEUR ET IMPORTATEUR D'EMPLOIS DU TEMPS")
    print("=" * 48)
    
    # Chemin du fichier (à adapter)
    file_path = r"C:\Users\HP\Downloads\Planning amphis_Printemps_24-25.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé: {file_path}")
        print("💡 Assurez-vous que le fichier est dans le bon répertoire")
        return
    
    # Étape 1: Analyser le fichier
    if analyze_excel_file(file_path):
        print("\n✅ Analyse terminée")
        
        # Étape 2: Lire et détecter le format
        df = pd.read_excel(file_path, sheet_name=0)
        format_detected = detect_schedule_format(df)
        
        # Étape 3: Importer
        print(f"\n🚀 Tentative d'import avec format: {format_detected}")
        success = import_from_custom_format(file_path)
        
        if success:
            print(f"\n🎉 Import réussi!")
            print(f"📱 Actualisez votre interface pour voir les nouveaux emplois du temps")
        else:
            print(f"\n💡 Suggestions pour corriger l'import:")
            print("1. Vérifiez le format des colonnes dans votre fichier Excel")
            print("2. Assurez-vous que les noms d'enseignants et de salles sont corrects")
            print("3. Adaptez le mapping des colonnes si nécessaire")

if __name__ == "__main__":
    main()
