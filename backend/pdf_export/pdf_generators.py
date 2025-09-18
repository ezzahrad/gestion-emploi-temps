from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime, timedelta
import os
import uuid
from io import BytesIO

class PDFGenerator:
    """Générateur PDF de base"""
    
    def __init__(self, template=None, **kwargs):
        self.template = template
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.page_format = A4
        self.orientation = 'portrait'
        self.margins = {
            'top': 20*mm,
            'bottom': 20*mm,
            'left': 20*mm,
            'right': 20*mm
        }
        
        if template:
            self.apply_template_settings(template)
    
    def setup_custom_styles(self):
        """Configurer les styles personnalisés"""
        # Style pour les titres
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb')
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937')
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Style pour les en-têtes de tableau
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def apply_template_settings(self, template):
        """Appliquer les paramètres du template"""
        # Format de page
        page_formats = {
            'A3': A3,
            'A4': A4,
            'Letter': letter
        }
        self.page_format = page_formats.get(template.page_format, A4)
        
        # Marges
        self.margins = {
            'top': template.margin_top * mm,
            'bottom': template.margin_bottom * mm,
            'left': template.margin_left * mm,
            'right': template.margin_right * mm
        }
    
    def create_document(self, filename):
        """Créer le document PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_format,
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom'],
            leftMargin=self.margins['left'],
            rightMargin=self.margins['right']
        )
        return doc, buffer
    
    def add_header(self, elements, title, subtitle=None):
        """Ajouter un en-tête"""
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        if subtitle:
            elements.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
    
    def add_info_table(self, elements, data, title=None):
        """Ajouter un tableau d'informations"""
        if title:
            elements.append(Paragraph(title, self.styles['CustomSubtitle']))
        
        table = Table(data, colWidths=[40*mm, 60*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
    

    
    def save_pdf(self, doc, buffer, filename):
        """Sauvegarder le PDF"""
        # Créer le répertoire s'il n'existe pas
        output_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_exports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(output_dir, unique_filename)
        
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        # Calculer la taille du fichier
        file_size = os.path.getsize(file_path)
        
        return file_path, file_size
    
    def generate(self, export_data, job=None):
        """Méthode générique pour générer un PDF"""
        # Cette méthode doit être implémentée par les sous-classes
        from io import BytesIO
        
        # Créer un PDF basique pour les tests
        buffer = BytesIO()
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 750, f"Export PDF - Type: {export_data.get('export_type', 'Unknown')}")
        c.drawString(100, 700, f"Généré le: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
        c.showPage()
        c.save()
        
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        
        return {
            'success': True,
            'pdf_data': pdf_data,
            'page_count': 1,
            'processing_time': 0.1
        }

class SchedulePDFGenerator(PDFGenerator):
    """Générateur pour les emplois du temps"""
    
    def generate_student_schedule(self, student, schedules, week_start=None, week_end=None):
        """Générer l'emploi du temps d'un étudiant"""
        filename = f"emploi_temps_{student.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        doc, buffer = self.create_document(filename)
        
        elements = []
        
        # En-tête
        title = f"Emploi du Temps - {student.full_name}"
        subtitle = f"Programme: {student.program.name if student.program else 'N/A'}"
        if week_start:
            subtitle += f" | Semaine du {week_start.strftime('%d/%m/%Y')}"
        
        self.add_header(elements, title, subtitle)
        
        # Informations étudiant
        info_data = [
            ['Nom complet:', student.full_name],
            ['Email:', student.email],
            ['Programme:', student.program.name if student.program else 'N/A'],
            ['Niveau:', student.program.get_level_display() if student.program else 'N/A']
        ]
        self.add_info_table(elements, info_data, "Informations Étudiant")
        
        # Emploi du temps
        if schedules:
            self.add_schedule_table(elements, schedules)
        else:
            elements.append(Paragraph("Aucun cours programmé pour cette période.", self.styles['CustomNormal']))
        
        # Construire le PDF
        doc.build(elements)
        
        return self.save_pdf(doc, buffer, filename)
    
    def add_schedule_table(self, elements, schedules):
        """Ajouter le tableau de l'emploi du temps"""
        elements.append(Paragraph("Planning des Cours", self.styles['CustomSubtitle']))
        
        # Organiser les cours par jour
        days_schedules = {}
        for schedule in schedules:
            day = schedule.day_name
            if day not in days_schedules:
                days_schedules[day] = []
            days_schedules[day].append(schedule)
        
        # Créer le tableau
        data = [['Jour', 'Heure', 'Matière', 'Enseignant', 'Salle']]
        
        for day in ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']:
            if day in days_schedules:
                day_schedules = sorted(days_schedules[day], key=lambda x: x.start_time)
                for i, schedule in enumerate(day_schedules):
                    row = [
                        day if i == 0 else '',
                        f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}",
                        schedule.subject_name,
                        schedule.teacher_name,
                        schedule.room_name
                    ]
                    data.append(row)
        
        # Style du tableau
        table = Table(data, colWidths=[25*mm, 30*mm, 50*mm, 40*mm, 25*mm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Contenu
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternance de couleurs pour les lignes
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))

class TranscriptPDFGenerator(PDFGenerator):
    """Générateur pour les relevés de notes"""
    
    def generate_student_transcript(self, student, transcript_data, include_details=True):
        """Générer le relevé de notes d'un étudiant"""
        filename = f"releve_notes_{student.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        doc, buffer = self.create_document(filename)
        
        elements = []
        
        # En-tête
        title = "Relevé de Notes Officiel"
        subtitle = f"Année Académique {transcript_data.get('academic_year', 'N/A')}"
        self.add_header(elements, title, subtitle)
        
        # Informations étudiant
        info_data = [
            ['Nom complet:', student.full_name],
            ['Numéro étudiant:', student.username],
            ['Programme:', transcript_data.get('program_name', 'N/A')],
            ['Niveau:', transcript_data.get('level', 'N/A')],
            ['Semestre:', f"S{transcript_data.get('semester', 'N/A')}"]
        ]
        self.add_info_table(elements, info_data, "Informations Étudiant")
        
        # Résultats académiques
        self.add_academic_results(elements, transcript_data, include_details)
        
        # Résumé
        self.add_transcript_summary(elements, transcript_data)
        
        # Construire le PDF
        doc.build(elements)
        
        return self.save_pdf(doc, buffer, filename)
    
    def add_academic_results(self, elements, transcript_data, include_details):
        """Ajouter les résultats académiques détaillés"""
        elements.append(Paragraph("Résultats par Matière", self.styles['CustomSubtitle']))
        
        subjects = transcript_data.get('subjects', [])
        
        if include_details:
            # Tableau détaillé avec toutes les notes
            for subject in subjects:
                self.add_subject_grades_table(elements, subject)
        else:
            # Tableau résumé
            self.add_subjects_summary_table(elements, subjects)
    
    def add_subject_grades_table(self, elements, subject):
        """Ajouter le tableau des notes pour une matière"""
        elements.append(Paragraph(f"{subject['subject_name']} ({subject['subject_code']})", 
                                self.styles['Heading3']))
        
        # Données du tableau
        data = [['Évaluation', 'Type', 'Date', 'Note', 'Coeff.', '%']]
        
        for grade in subject.get('grades', []):
            data.append([
                grade['evaluation_name'],
                grade['evaluation_type'],
                grade['evaluation_date'],
                f"{grade['grade_value']}/{grade['max_grade']}",
                grade['coefficient'],
                f"{grade['percentage']:.1f}%"
            ])
        
        # Ligne de moyenne
        data.append([
            'MOYENNE', '', '', '', '',
            f"{subject['weighted_average']:.2f}/20 ({subject['grade_letter']})"
        ])
        
        table = Table(data, colWidths=[40*mm, 20*mm, 25*mm, 20*mm, 15*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (-2, -1), (-1, -1), colors.HexColor('#fef3c7')),
            ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 8))
    
    def add_transcript_summary(self, elements, transcript_data):
        """Ajouter le résumé du relevé"""
        elements.append(PageBreak())
        elements.append(Paragraph("Résumé Académique", self.styles['CustomSubtitle']))
        
        summary_data = [
            ['Moyenne Générale:', f"{transcript_data.get('overall_average', 'N/A')}/20"],
            ['GPA:', f"{transcript_data.get('gpa', 'N/A')}/4.0"],
            ['Note Lettrée:', transcript_data.get('grade_letter', 'N/A')],
            ['Crédits Acquis:', f"{transcript_data.get('acquired_credits', 0)}/{transcript_data.get('total_credits', 0)}"],
            ['Classement:', f"{transcript_data.get('rank', 'N/A')}/{transcript_data.get('total_students', 'N/A')}"]
        ]
        
        self.add_info_table(elements, summary_data)
        
        # Ajouter la date de génération
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['Normal']
        ))

class AbsenceReportPDFGenerator(PDFGenerator):
    """Générateur pour les rapports d'absence"""
    
    def generate_absence_report(self, student, absences, statistics, period_start, period_end):
        """Générer un rapport d'absences"""
        filename = f"rapport_absences_{student.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        doc, buffer = self.create_document(filename)
        
        elements = []
        
        # En-tête
        title = "Rapport d'Absences"
        subtitle = f"Période: {period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"
        self.add_header(elements, title, subtitle)
        
        # Informations étudiant
        info_data = [
            ['Nom complet:', student.full_name],
            ['Programme:', student.program.name if student.program else 'N/A'],
            ['Période:', f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"]
        ]
        self.add_info_table(elements, info_data, "Informations Étudiant")
        
        # Statistiques
        self.add_absence_statistics(elements, statistics)
        
        # Liste des absences
        if absences:
            self.add_absences_table(elements, absences)
        
        # Construire le PDF
        doc.build(elements)
        
        return self.save_pdf(doc, buffer, filename)
    
    def add_absence_statistics(self, elements, statistics):
        """Ajouter les statistiques d'absence"""
        elements.append(Paragraph("Statistiques", self.styles['CustomSubtitle']))
        
        stats_data = [
            ['Total absences:', str(statistics.get('total_absences', 0))],
            ['Absences justifiées:', str(statistics.get('justified_absences', 0))],
            ['Absences non justifiées:', str(statistics.get('unjustified_absences', 0))],
            ['Taux d\'absence:', f"{statistics.get('absence_rate', 0):.1f}%"],
            ['Rattrapages en attente:', str(statistics.get('pending_makeups', 0))],
            ['Rattrapages terminés:', str(statistics.get('completed_makeups', 0))]
        ]
        
        self.add_info_table(elements, stats_data)
    
    def add_absences_table(self, elements, absences):
        """Ajouter le tableau des absences"""
        elements.append(Paragraph("Détail des Absences", self.styles['CustomSubtitle']))
        
        data = [['Date', 'Matière', 'Type', 'Statut', 'Rattrapage']]
        
        for absence in absences:
            data.append([
                absence.absence_date.strftime('%d/%m/%Y'),
                absence.schedule.subject_name,
                absence.get_absence_type_display(),
                absence.get_status_display(),
                'Oui' if absence.is_makeup_required else 'Non'
            ])
        
        table = Table(data, colWidths=[25*mm, 50*mm, 30*mm, 25*mm, 20*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        elements.append(table)

class BulkExportPDFGenerator(PDFGenerator):
    """Générateur pour les exports en masse"""
    
    def generate_bulk_schedules(self, students, schedules_data):
        """Générer plusieurs emplois du temps"""
        results = []
        
        for student in students:
            student_schedules = schedules_data.get(student.id, [])
            schedule_generator = SchedulePDFGenerator(template=self.template)
            try:
                file_path, file_size = schedule_generator.generate_student_schedule(
                    student, student_schedules
                )
                results.append({
                    'student_id': student.id,
                    'success': True,
                    'file_path': file_path,
                    'file_size': file_size
                })
            except Exception as e:
                results.append({
                    'student_id': student.id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def generate_bulk_transcripts(self, students, transcripts_data):
        """Générer plusieurs relevés de notes"""
        results = []
        
        for student in students:
            student_transcript = transcripts_data.get(student.id, {})
            transcript_generator = TranscriptPDFGenerator(template=self.template)
            try:
                file_path, file_size = transcript_generator.generate_student_transcript(
                    student, student_transcript
                )
                results.append({
                    'student_id': student.id,
                    'success': True,
                    'file_path': file_path,
                    'file_size': file_size
                })
            except Exception as e:
                results.append({
                    'student_id': student.id,
                    'success': False,
                    'error': str(e)
                })
        
        return results

# Factory pour créer les générateurs appropriés
class PDFGeneratorFactory:
    """Factory pour créer les bons générateurs PDF"""
    
    generators = {
        'schedule': SchedulePDFGenerator,
        'transcript': TranscriptPDFGenerator,
        'absence_report': AbsenceReportPDFGenerator,
        'attendance_report': AbsenceReportPDFGenerator,
        'teacher_schedule': SchedulePDFGenerator,
        'room_schedule': SchedulePDFGenerator,
        'bulk_schedules': BulkExportPDFGenerator,
        'bulk_transcripts': BulkExportPDFGenerator,
    }
    
    @classmethod
    def create_generator(cls, export_type, template=None):
        """Créer le générateur approprié"""
        generator_class = cls.generators.get(export_type, PDFGenerator)
        return generator_class(template=template)
