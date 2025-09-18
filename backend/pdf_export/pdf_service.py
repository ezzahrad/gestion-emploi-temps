from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import PDFExportJob, PDFTemplate, PDFExportSettings
from .pdf_generators import PDFGeneratorFactory
from schedule.models import Schedule
from grades.models import Grade, SubjectGradeSummary, StudentTranscript
from absences.models import Absence, StudentAbsenceStatistics
from core.models import Program, Department, Room
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class PDFExportService:
    """Service pour gérer les exports PDF"""
    
    def __init__(self):
        self.settings = PDFExportSettings.objects.first()
    
    def process_export(self, job_id):
        """Traiter un export PDF"""
        try:
            job = PDFExportJob.objects.get(id=job_id)
            job.mark_as_processing()
            
            # Choisir la méthode selon le type d'export
            export_methods = {
                'schedule': self._generate_student_schedule,
                'teacher_schedule': self._generate_teacher_schedule,
                'room_schedule': self._generate_room_schedule,
                'transcript': self._generate_student_transcript,
                'absence_report': self._generate_absence_report,
                'attendance_report': self._generate_attendance_report,
            }
            
            method = export_methods.get(job.export_type)
            if not method:
                raise ValueError(f"Type d'export non supporté: {job.export_type}")
            
            file_path, file_size, page_count = method(job)
            
            job.mark_as_completed(
                file_path=file_path,
                file_size=file_size,
                page_count=page_count,
                message="Export généré avec succès"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export PDF {job_id}: {str(e)}")
            job.mark_as_failed(str(e), {'exception_type': type(e).__name__})
    
    def process_bulk_export(self, job_id):
        """Traiter un export en masse"""
        try:
            job = PDFExportJob.objects.get(id=job_id)
            job.mark_as_processing()
            
            if job.export_type == 'bulk_schedules':
                file_path, file_size, page_count = self._generate_bulk_schedules(job)
            elif job.export_type == 'bulk_transcripts':
                file_path, file_size, page_count = self._generate_bulk_transcripts(job)
            else:
                raise ValueError(f"Type d'export en masse non supporté: {job.export_type}")
            
            job.mark_as_completed(
                file_path=file_path,
                file_size=file_size,
                page_count=page_count,
                message="Export en masse généré avec succès"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export en masse {job_id}: {str(e)}")
            job.mark_as_failed(str(e), {'exception_type': type(e).__name__})
    
    def _generate_student_schedule(self, job):
        """Générer l'emploi du temps d'un étudiant"""
        params = job.export_parameters
        student_id = params.get('student_id')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        # Récupérer l'étudiant
        student = User.objects.get(id=student_id, role='student')
        
        # Récupérer les emplois du temps
        schedules_query = Schedule.objects.filter(program=student.program)
        
        if start_date and end_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            schedules_query = schedules_query.filter(
                week_start__gte=start_date,
                week_start__lte=end_date
            )
        
        schedules = schedules_query.order_by('day_of_week', 'start_time')
        
        # Générer le PDF
        generator = PDFGeneratorFactory.create_generator('schedule', job.template)
        file_path, file_size = generator.generate_student_schedule(
            student=student,
            schedules=schedules,
            week_start=start_date,
            week_end=end_date
        )
        
        # Estimer le nombre de pages (basique)
        page_count = max(1, len(schedules) // 10 + 1)
        
        return file_path, file_size, page_count
    
    def _generate_teacher_schedule(self, job):
        """Générer le planning d'un enseignant"""
        params = job.export_parameters
        teacher_id = params.get('teacher_id')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        # Récupérer l'enseignant
        teacher = User.objects.get(id=teacher_id, role='teacher')
        
        # Récupérer les emplois du temps
        schedules_query = Schedule.objects.filter(teacher=teacher_id)
        
        if start_date and end_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            schedules_query = schedules_query.filter(
                week_start__gte=start_date,
                week_start__lte=end_date
            )
        
        schedules = schedules_query.order_by('day_of_week', 'start_time')
        
        # Générer le PDF (utiliser le générateur de base pour l'instant)
        generator = PDFGeneratorFactory.create_generator('schedule', job.template)
        
        # Adapter pour l'enseignant
        filename = f"planning_enseignant_{teacher.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        doc, buffer = generator.create_document(filename)
        
        elements = []
        generator.add_header(elements, f"Planning Enseignant - {teacher.full_name}")
        
        if schedules:
            generator.add_schedule_table(elements, schedules)
        else:
            from reportlab.platypus import Paragraph
            elements.append(Paragraph("Aucun cours programmé pour cette période.", generator.styles['CustomNormal']))
        
        doc.build(elements)
        file_path, file_size = generator.save_pdf(doc, buffer, filename)
        
        page_count = max(1, len(schedules) // 10 + 1)
        
        return file_path, file_size, page_count
    
    def _generate_room_schedule(self, job):
        """Générer le planning d'une salle"""
        params = job.export_parameters
        room_id = params.get('room_id')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        # Récupérer la salle
        room = Room.objects.get(id=room_id)
        
        # Récupérer les emplois du temps
        schedules_query = Schedule.objects.filter(room=room_id)
        
        if start_date and end_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            schedules_query = schedules_query.filter(
                week_start__gte=start_date,
                week_start__lte=end_date
            )
        
        schedules = schedules_query.order_by('day_of_week', 'start_time')
        
        # Générer le PDF
        generator = PDFGeneratorFactory.create_generator('schedule', job.template)
        
        filename = f"planning_salle_{room.code}_{timezone.now().strftime('%Y%m%d')}.pdf"
        doc, buffer = generator.create_document(filename)
        
        elements = []
        generator.add_header(elements, f"Planning Salle - {room.name}")
        
        # Info salle
        info_data = [
            ['Nom:', room.name],
            ['Code:', room.code],
            ['Type:', room.get_room_type_display()],
            ['Capacité:', f"{room.capacity} personnes"],
            ['Département:', room.department_name]
        ]
        generator.add_info_table(elements, info_data, "Informations Salle")
        
        if schedules:
            generator.add_schedule_table(elements, schedules)
        else:
            from reportlab.platypus import Paragraph
            elements.append(Paragraph("Aucun cours programmé pour cette période.", generator.styles['CustomNormal']))
        
        doc.build(elements)
        file_path, file_size = generator.save_pdf(doc, buffer, filename)
        
        page_count = max(1, len(schedules) // 10 + 2)  # +1 pour info salle
        
        return file_path, file_size, page_count
    
    def _generate_student_transcript(self, job):
        """Générer le relevé de notes d'un étudiant"""
        params = job.export_parameters
        student_id = params.get('student_id')
        include_details = params.get('include_details', True)
        academic_year = params.get('academic_year')
        semester = params.get('semester')
        
        # Récupérer l'étudiant
        student = User.objects.get(id=student_id, role='student')
        
        # Récupérer les données du relevé
        transcript_data = self._prepare_transcript_data(student, academic_year, semester)
        
        # Générer le PDF
        generator = PDFGeneratorFactory.create_generator('transcript', job.template)
        file_path, file_size = generator.generate_student_transcript(
            student=student,
            transcript_data=transcript_data,
            include_details=include_details
        )
        
        # Estimer le nombre de pages
        subjects_count = len(transcript_data.get('subjects', []))
        page_count = max(2, subjects_count // 3 + 2)  # 3 matières par page environ
        
        return file_path, file_size, page_count
    
    def _generate_absence_report(self, job):
        """Générer un rapport d'absences"""
        params = job.export_parameters
        student_id = params.get('student_id')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        # Récupérer l'étudiant
        student = User.objects.get(id=student_id, role='student')
        
        # Préparer les dates
        if start_date and end_date:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Par défaut, derniers 3 mois
            end_date = timezone.now().date()
            start_date = end_date - timezone.timedelta(days=90)
        
        # Récupérer les absences
        absences = Absence.objects.filter(
            student=student,
            absence_date__range=[start_date, end_date]
        ).order_by('-absence_date')
        
        # Récupérer les statistiques
        stats, created = StudentAbsenceStatistics.objects.get_or_create(student=student)
        if created or not stats.last_calculated:
            stats.calculate_statistics(start_date, end_date)
        
        statistics = {
            'total_absences': stats.total_absences,
            'justified_absences': stats.justified_absences,
            'unjustified_absences': stats.unjustified_absences,
            'absence_rate': stats.absence_rate,
            'pending_makeups': stats.pending_makeups,
            'completed_makeups': stats.completed_makeups
        }
        
        # Générer le PDF
        generator = PDFGeneratorFactory.create_generator('absence_report', job.template)
        file_path, file_size = generator.generate_absence_report(
            student=student,
            absences=absences,
            statistics=statistics,
            period_start=start_date,
            period_end=end_date
        )
        
        page_count = max(1, len(absences) // 15 + 2)  # 15 absences par page environ
        
        return file_path, file_size, page_count
    
    def _generate_attendance_report(self, job):
        """Générer un rapport de présences"""
        # Similaire au rapport d'absences mais focalisé sur la présence
        # À implémenter selon les besoins spécifiques
        pass
    
    def _generate_bulk_schedules(self, job):
        """Générer les emplois du temps en masse"""
        params = job.export_parameters
        program_ids = params.get('program_ids', [])
        department_ids = params.get('department_ids', [])
        student_ids = params.get('student_ids', [])
        combine_in_single_file = params.get('combine_in_single_file', False)
        
        # Récupérer les étudiants concernés
        students_query = User.objects.filter(role='student')
        
        if student_ids:
            students_query = students_query.filter(id__in=student_ids)
        elif program_ids:
            students_query = students_query.filter(program__in=program_ids)
        elif department_ids:
            students_query = students_query.filter(program__department__in=department_ids)
        
        students = students_query.order_by('last_name', 'first_name')
        
        if combine_in_single_file:
            # Générer un seul fichier avec tous les emplois du temps
            return self._generate_combined_schedules(job, students)
        else:
            # Générer un fichier ZIP avec un PDF par étudiant
            return self._generate_separate_schedules(job, students)
    
    def _generate_bulk_transcripts(self, job):
        """Générer les relevés de notes en masse"""
        # Similaire à bulk_schedules mais pour les relevés
        pass
    
    def _prepare_transcript_data(self, student, academic_year=None, semester=None):
        """Préparer les données du relevé de notes"""
        # Récupérer les résumés par matière
        summaries = SubjectGradeSummary.objects.filter(
            student=student,
            is_validated=True
        ).select_related('subject')
        
        subjects_data = []
        total_credits = 0
        total_weighted_points = 0
        total_coefficients = 0
        
        for summary in summaries:
            # Récupérer les notes détaillées
            grades = Grade.objects.filter(
                student=student,
                evaluation__subject=summary.subject,
                is_published=True
            ).select_related('evaluation').order_by('-evaluation__evaluation_date')
            
            grades_data = []
            for grade in grades:
                grades_data.append({
                    'evaluation_name': grade.evaluation.name,
                    'evaluation_type': grade.evaluation.get_evaluation_type_display(),
                    'evaluation_date': grade.evaluation.evaluation_date.strftime('%d/%m/%Y'),
                    'grade_value': float(grade.grade_value),
                    'max_grade': float(grade.evaluation.max_grade),
                    'percentage': float(grade.percentage),
                    'coefficient': float(grade.evaluation.coefficient)
                })
            
            subjects_data.append({
                'subject_name': summary.subject.name,
                'subject_code': summary.subject.code,
                'subject_credits': summary.subject.credits,
                'average_grade': float(summary.average_grade) if summary.average_grade else 0,
                'weighted_average': float(summary.weighted_average) if summary.weighted_average else 0,
                'grade_letter': summary.grade_letter,
                'grades': grades_data
            })
            
            # Calculs pour la moyenne générale
            if summary.weighted_average and summary.subject.credits:
                total_credits += summary.subject.credits
                total_weighted_points += float(summary.weighted_average) * summary.subject.credits
                total_coefficients += float(summary.total_coefficient)
        
        # Calculs finaux
        overall_average = (total_weighted_points / total_credits) if total_credits > 0 else 0
        gpa = self._calculate_gpa(overall_average)
        
        return {
            'student_name': student.full_name,
            'student_id': student.username,
            'program_name': student.program.name if student.program else 'N/A',
            'program_code': student.program.code if student.program else 'N/A',
            'level': student.program.get_level_display() if student.program else 'N/A',
            'department_name': student.program.department.name if student.program else 'N/A',
            'academic_year': academic_year or '2024-2025',
            'semester': semester or 1,
            'subjects': subjects_data,
            'overall_average': overall_average,
            'gpa': gpa,
            'grade_letter': self._get_grade_letter(overall_average),
            'total_credits': total_credits,
            'acquired_credits': sum(s['subject_credits'] for s in subjects_data if s['weighted_average'] >= 10),
            'rank': None,  # À calculer si nécessaire
            'total_students': None  # À calculer si nécessaire
        }
    
    def _calculate_gpa(self, average):
        """Calculer le GPA à partir de la moyenne sur 20"""
        if average >= 16:
            return 4.0
        elif average >= 14:
            return 3.5
        elif average >= 12:
            return 3.0
        elif average >= 10:
            return 2.5
        elif average >= 8:
            return 2.0
        else:
            return 1.0
    
    def _get_grade_letter(self, average):
        """Obtenir la note lettrée"""
        if average >= 16:
            return 'A'
        elif average >= 14:
            return 'B+'
        elif average >= 12:
            return 'B'
        elif average >= 10:
            return 'C+'
        elif average >= 8:
            return 'C'
        else:
            return 'F'
    
    def _generate_combined_schedules(self, job, students):
        """Générer un fichier combiné pour tous les emplois du temps"""
        # À implémenter
        pass
    
    def _generate_separate_schedules(self, job, students):
        """Générer des fichiers séparés pour chaque emploi du temps"""
        # À implémenter - créer un ZIP
        pass
