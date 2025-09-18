from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import (
    AbsencePolicy, Absence, MakeupSession, 
    AttendanceRecord, StudentAbsenceStatistics
)

@admin.register(AbsencePolicy)
class AbsencePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'max_unjustified_absences', 'max_total_absences_percentage', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'is_default')
        }),
        ('Limites d\'absence', {
            'fields': ('max_unjustified_absences', 'max_total_absences_percentage')
        }),
        ('Délais (en heures/jours)', {
            'fields': ('justification_deadline_hours', 'makeup_request_deadline_days')
        }),
        ('Règles de justification', {
            'fields': ('medical_justification_required', 'family_emergency_accepted')
        }),
    )

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'subject_name', 'absence_date', 'absence_type_display', 
        'status_display', 'is_makeup_required', 'makeup_completed', 'justification_status'
    ]
    list_filter = [
        'absence_type', 'status', 'is_makeup_required', 'makeup_completed',
        'absence_date', 'reported_at'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__username',
        'schedule__subject_name', 'reason'
    ]
    date_hierarchy = 'absence_date'
    
    fieldsets = (
        ('Étudiant et Cours', {
            'fields': ('student', 'schedule', 'absence_date')
        }),
        ('Détails de l\'absence', {
            'fields': ('absence_type', 'reason', 'justification_document')
        }),
        ('Statut et Rattrapage', {
            'fields': ('status', 'is_makeup_required', 'makeup_completed')
        }),
        ('Approbation', {
            'fields': ('approved_by', 'approved_at', 'admin_comments'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('reported_by', 'reported_at', 'justification_deadline'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['reported_at', 'approved_at', 'justification_deadline']
    
    actions = ['approve_absences', 'reject_absences', 'require_makeup']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def subject_name(self, obj):
        return obj.schedule.subject_name
    subject_name.short_description = 'Matière'
    
    def absence_type_display(self, obj):
        colors = {
            'unjustified': 'red',
            'medical': 'blue',
            'family': 'orange',
            'personal': 'purple',
            'transportation': 'brown',
            'other': 'gray'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.absence_type, 'black'),
            obj.get_absence_type_display()
        )
    absence_type_display.short_description = 'Type'
    
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'auto_approved': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'
    
    def justification_status(self, obj):
        if obj.justification_document:
            return format_html(
                '<a href="{}" target="_blank">📄 Voir</a>',
                obj.justification_document.url
            )
        elif obj.is_justification_overdue():
            return format_html('<span style="color: red;">⏰ Retard</span>')
        else:
            return format_html('<span style="color: gray;">❌ Aucune</span>')
    justification_status.short_description = 'Justification'
    
    def approve_absences(self, request, queryset):
        count = 0
        for absence in queryset.filter(status='pending'):
            absence.status = 'approved'
            absence.approved_by = request.user
            absence.approved_at = timezone.now()
            absence.save()
            count += 1
        self.message_user(request, f'{count} absences approuvées.')
    approve_absences.short_description = 'Approuver les absences sélectionnées'
    
    def reject_absences(self, request, queryset):
        count = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{count} absences rejetées.')
    reject_absences.short_description = 'Rejeter les absences sélectionnées'
    
    def require_makeup(self, request, queryset):
        count = queryset.update(is_makeup_required=True)
        self.message_user(request, f'{count} absences marquées comme nécessitant un rattrapage.')
    require_makeup.short_description = 'Marquer comme nécessitant un rattrapage'

@admin.register(MakeupSession)
class MakeupSessionAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'subject_name', 'makeup_date', 'makeup_time', 
        'room_name', 'teacher_name', 'status_display', 'attendance_confirmed'
    ]
    list_filter = [
        'status', 'attendance_confirmed', 'makeup_date', 'created_at'
    ]
    search_fields = [
        'absence__student__first_name', 'absence__student__last_name',
        'teacher__first_name', 'teacher__last_name', 'room__name'
    ]
    date_hierarchy = 'makeup_date'
    
    fieldsets = (
        ('Absence concernée', {
            'fields': ('absence',)
        }),
        ('Programmation', {
            'fields': ('makeup_date', 'makeup_start_time', 'makeup_end_time', 'room', 'teacher')
        }),
        ('Statut et Suivi', {
            'fields': ('status', 'attendance_confirmed')
        }),
        ('Évaluation', {
            'fields': ('makeup_grade', 'is_successful'),
            'classes': ('collapse',)
        }),
        ('Commentaires', {
            'fields': ('session_notes', 'student_feedback', 'teacher_feedback'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('scheduled_by', 'confirmed_by', 'confirmed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['confirmed_at']
    
    actions = ['confirm_sessions', 'mark_completed', 'cancel_sessions']
    
    def student_name(self, obj):
        return obj.absence.student.full_name
    student_name.short_description = 'Étudiant'
    
    def subject_name(self, obj):
        return obj.absence.schedule.subject_name
    subject_name.short_description = 'Matière'
    
    def makeup_time(self, obj):
        return f"{obj.makeup_start_time.strftime('%H:%M')} - {obj.makeup_end_time.strftime('%H:%M')}"
    makeup_time.short_description = 'Horaire'
    
    def room_name(self, obj):
        return obj.room.name
    room_name.short_description = 'Salle'
    
    def teacher_name(self, obj):
        return obj.teacher.full_name
    teacher_name.short_description = 'Enseignant'
    
    def status_display(self, obj):
        colors = {
            'scheduled': 'blue',
            'confirmed': 'green',
            'completed': 'darkgreen',
            'cancelled': 'red',
            'rescheduled': 'orange'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'
    
    def confirm_sessions(self, request, queryset):
        count = queryset.filter(status='scheduled').update(
            status='confirmed',
            confirmed_by=request.user,
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{count} sessions confirmées.')
    confirm_sessions.short_description = 'Confirmer les sessions'
    
    def mark_completed(self, request, queryset):
        count = 0
        for session in queryset.filter(status__in=['scheduled', 'confirmed']):
            session.mark_completed(attendance_confirmed=True)
            count += 1
        self.message_user(request, f'{count} sessions marquées comme terminées.')
    mark_completed.short_description = 'Marquer comme terminées'
    
    def cancel_sessions(self, request, queryset):
        count = queryset.exclude(status='completed').update(status='cancelled')
        self.message_user(request, f'{count} sessions annulées.')
    cancel_sessions.short_description = 'Annuler les sessions'

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'subject_name', 'schedule_date', 'status_display',
        'arrival_display', 'departure_display', 'minutes_late', 'is_validated'
    ]
    list_filter = [
        'status', 'is_validated', 'schedule__week_start', 'recorded_at'
    ]
    search_fields = [
        'student__first_name', 'student__last_name',
        'schedule__subject_name', 'notes'
    ]
    date_hierarchy = 'schedule__week_start'
    
    fieldsets = (
        ('Étudiant et Cours', {
            'fields': ('student', 'schedule')
        }),
        ('Présence', {
            'fields': ('status', 'arrival_time', 'departure_time')
        }),
        ('Calculs automatiques', {
            'fields': ('minutes_late', 'minutes_early_departure'),
            'classes': ('collapse',)
        }),
        ('Commentaires et Validation', {
            'fields': ('notes', 'is_validated', 'validated_by', 'validated_at')
        }),
        ('Métadonnées', {
            'fields': ('recorded_by', 'recorded_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['minutes_late', 'minutes_early_departure', 'validated_at', 'recorded_at']
    
    actions = ['validate_records', 'mark_as_present', 'mark_as_absent']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def subject_name(self, obj):
        return obj.schedule.subject_name
    subject_name.short_description = 'Matière'
    
    def schedule_date(self, obj):
        return obj.schedule.week_start.strftime('%d/%m/%Y')
    schedule_date.short_description = 'Date'
    
    def status_display(self, obj):
        colors = {
            'present': 'green',
            'absent': 'red',
            'late': 'orange',
            'excused': 'blue',
            'left_early': 'purple'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'
    
    def arrival_display(self, obj):
        if obj.arrival_time:
            color = 'red' if obj.minutes_late > 0 else 'green'
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                obj.arrival_time.strftime('%H:%M')
            )
        return '-'
    arrival_display.short_description = 'Arrivée'
    
    def departure_display(self, obj):
        if obj.departure_time:
            color = 'red' if obj.minutes_early_departure > 0 else 'green'
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                obj.departure_time.strftime('%H:%M')
            )
        return '-'
    departure_display.short_description = 'Départ'
    
    def validate_records(self, request, queryset):
        count = queryset.update(
            is_validated=True,
            validated_by=request.user,
            validated_at=timezone.now()
        )
        self.message_user(request, f'{count} enregistrements validés.')
    validate_records.short_description = 'Valider les enregistrements'

@admin.register(StudentAbsenceStatistics)
class StudentAbsenceStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'total_absences', 'absence_rate_display', 
        'justified_rate_display', 'risk_level_display', 'last_calculated'
    ]
    list_filter = [
        'risk_level', 'is_at_risk', 'last_calculated'
    ]
    search_fields = [
        'student__first_name', 'student__last_name'
    ]
    
    fieldsets = (
        ('Étudiant', {
            'fields': ('student',)
        }),
        ('Statistiques d\'absence', {
            'fields': (
                'total_absences', 'justified_absences', 'unjustified_absences',
                'pending_absences', 'absence_rate', 'justified_rate'
            )
        }),
        ('Rattrapages', {
            'fields': ('pending_makeups', 'completed_makeups', 'failed_makeups')
        }),
        ('Évaluation du risque', {
            'fields': ('is_at_risk', 'risk_level')
        }),
        ('Période', {
            'fields': ('period_start', 'period_end', 'last_calculated'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'total_absences', 'justified_absences', 'unjustified_absences',
        'pending_absences', 'absence_rate', 'justified_rate',
        'pending_makeups', 'completed_makeups', 'failed_makeups',
        'is_at_risk', 'risk_level', 'last_calculated'
    ]
    
    actions = ['recalculate_statistics']
    
    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Étudiant'
    
    def absence_rate_display(self, obj):
        color = 'red' if obj.absence_rate > 25 else 'orange' if obj.absence_rate > 15 else 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            obj.absence_rate
        )
    absence_rate_display.short_description = 'Taux d\'absence'
    
    def justified_rate_display(self, obj):
        color = 'green' if obj.justified_rate > 80 else 'orange' if obj.justified_rate > 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            obj.justified_rate
        )
    justified_rate_display.short_description = 'Taux justifié'
    
    def risk_level_display(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.risk_level, 'black'),
            obj.get_risk_level_display()
        )
    risk_level_display.short_description = 'Niveau de risque'
    
    def recalculate_statistics(self, request, queryset):
        count = 0
        for stats in queryset:
            stats.calculate_statistics()
            count += 1
        self.message_user(request, f'{count} statistiques recalculées.')
    recalculate_statistics.short_description = 'Recalculer les statistiques'
