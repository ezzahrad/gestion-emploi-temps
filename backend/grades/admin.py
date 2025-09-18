from datetime import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import GradeScale, Evaluation, Grade, SubjectGradeSummary, StudentTranscript

@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'a_min', 'b_min', 'c_min', 'd_min', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'is_default')
        }),
        ('Échelle de notation (%)', {
            'fields': (
                ('a_plus_min', 'a_min'),
                ('b_plus_min', 'b_min'),
                ('c_plus_min', 'c_min'),
                ('d_plus_min', 'd_min'),
            )
        }),
    )

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['name', 'evaluation_type', 'subject', 'evaluation_date', 'max_grade', 'coefficient', 'is_published', 'grades_count']
    list_filter = ['evaluation_type', 'is_published', 'evaluation_date', 'subject__department']
    search_fields = ['name', 'subject__name', 'subject__code']
    date_hierarchy = 'evaluation_date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'evaluation_type', 'subject', 'description')
        }),
        ('Configuration', {
            'fields': ('evaluation_date', 'max_grade', 'coefficient', 'is_published')
        }),
        ('Métadonnées', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def grades_count(self, obj):
        count = obj.grades.count()
        total_students = obj.subject.program.first().students_count if obj.subject.program.exists() else 0
        return format_html(
            '<span style="color: {};">{}/{}</span>',
            'green' if count == total_students else 'orange',
            count,
            total_students
        )
    grades_count.short_description = 'Notes saisies'

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'evaluation_name', 'subject_name', 'grade_display', 'percentage_display', 'grade_letter', 'is_published', 'created_at']
    list_filter = ['is_published', 'grade_letter', 'evaluation__evaluation_type', 'evaluation__subject__department', 'created_at']
    search_fields = ['student__first_name', 'student__last_name', 'evaluation__name', 'evaluation__subject__name']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Étudiant et Évaluation', {
            'fields': ('student', 'evaluation')
        }),
        ('Note', {
            'fields': ('grade_value', 'comments')
        }),
        ('Publication', {
            'fields': ('is_published', 'published_at')
        }),
        ('Informations calculées', {
            'fields': ('percentage', 'grade_letter'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('graded_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['percentage', 'grade_letter', 'graded_by', 'published_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.graded_by = request.user
        super().save_model(request, obj, form, change)
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def evaluation_name(self, obj):
        return obj.evaluation.name
    evaluation_name.short_description = 'Évaluation'
    
    def subject_name(self, obj):
        return obj.evaluation.subject.name
    subject_name.short_description = 'Matière'
    
    def grade_display(self, obj):
        return f"{obj.grade_value}/{obj.evaluation.max_grade}"
    grade_display.short_description = 'Note'
    
    def percentage_display(self, obj):
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            'green' if obj.percentage >= 60 else 'red',
            obj.percentage
        )
    percentage_display.short_description = 'Pourcentage'

@admin.register(SubjectGradeSummary)
class SubjectGradeSummaryAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'subject_name', 'average_display', 'weighted_average_display', 'grade_letter', 'is_validated', 'updated_at']
    list_filter = ['is_validated', 'grade_letter', 'subject__department', 'updated_at']
    search_fields = ['student__first_name', 'student__last_name', 'subject__name']
    
    readonly_fields = ['average_grade', 'weighted_average', 'grade_letter', 'total_evaluations', 'published_evaluations', 'total_coefficient']
    
    actions = ['recalculate_averages', 'validate_summaries']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def subject_name(self, obj):
        return obj.subject.name
    subject_name.short_description = 'Matière'
    
    def average_display(self, obj):
        if obj.average_grade:
            return format_html(
                '<span style="color: {};">{:.2f}/20</span>',
                'green' if obj.average_grade >= 10 else 'red',
                obj.average_grade
            )
        return '-'
    average_display.short_description = 'Moyenne simple'
    
    def weighted_average_display(self, obj):
        if obj.weighted_average:
            return format_html(
                '<span style="color: {};">{:.2f}/20</span>',
                'green' if obj.weighted_average >= 10 else 'red',
                obj.weighted_average
            )
        return '-'
    weighted_average_display.short_description = 'Moyenne pondérée'
    
    def recalculate_averages(self, request, queryset):
        count = 0
        for summary in queryset:
            summary.calculate_averages()
            count += 1
        self.message_user(request, f'{count} moyennes recalculées avec succès.')
    recalculate_averages.short_description = 'Recalculer les moyennes'
    
    def validate_summaries(self, request, queryset):
        count = queryset.update(
            is_validated=True,
            validated_by=request.user,
            validated_at=timezone.now()
        )
        self.message_user(request, f'{count} résumés validés avec succès.')
    validate_summaries.short_description = 'Valider les résumés'

@admin.register(StudentTranscript)
class StudentTranscriptAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'program_name', 'semester_display', 'overall_average_display', 'gpa_display', 'credits_display', 'is_finalized']
    list_filter = ['is_finalized', 'program', 'semester', 'academic_year']
    search_fields = ['student__first_name', 'student__last_name', 'program__name']
    
    readonly_fields = ['overall_average', 'gpa', 'grade_letter', 'total_credits', 'acquired_credits', 'rank', 'total_students']
    
    actions = ['recalculate_gpa', 'finalize_transcripts']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def program_name(self, obj):
        return obj.program.name
    program_name.short_description = 'Programme'
    
    def semester_display(self, obj):
        return f"S{obj.semester} {obj.academic_year}"
    semester_display.short_description = 'Semestre'
    
    def overall_average_display(self, obj):
        if obj.overall_average:
            return format_html(
                '<span style="color: {};">{:.2f}/20</span>',
                'green' if obj.overall_average >= 10 else 'red',
                obj.overall_average
            )
        return '-'
    overall_average_display.short_description = 'Moyenne générale'
    
    def gpa_display(self, obj):
        if obj.gpa:
            return format_html(
                '<span style="color: {};">{:.2f}/4.0</span>',
                'green' if obj.gpa >= 2.0 else 'red',
                obj.gpa
            )
        return '-'
    gpa_display.short_description = 'GPA'
    
    def credits_display(self, obj):
        return f"{obj.acquired_credits}/{obj.total_credits}"
    credits_display.short_description = 'Crédits'
    
    def recalculate_gpa(self, request, queryset):
        count = 0
        for transcript in queryset:
            transcript.calculate_gpa()
            count += 1
        self.message_user(request, f'{count} GPA recalculés avec succès.')
    recalculate_gpa.short_description = 'Recalculer les GPA'
    
    def finalize_transcripts(self, request, queryset):
        count = queryset.update(
            is_finalized=True,
            finalized_by=request.user,
            finalized_at=timezone.now()
        )
        self.message_user(request, f'{count} relevés finalisés avec succès.')
    finalize_transcripts.short_description = 'Finaliser les relevés'
