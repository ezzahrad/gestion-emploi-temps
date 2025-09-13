from django.contrib import admin
from .models import Schedule, Absence, MakeupSession

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject_name', 'teacher_name', 'room_name', 'program_name', 'day_name', 'time_range', 'week_period', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'subject', 'room', 'program', 'created_at')
    search_fields = ('title', 'subject__name', 'teacher__user__first_name', 'teacher__user__last_name', 'room__name')
    ordering = ('day_of_week', 'start_time', 'subject')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'subject', 'teacher', 'room', 'program')
        }),
        ('Horaires', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'week_start', 'week_end')
        }),
        ('Options', {
            'fields': ('is_active', 'notes', 'created_by')
        }),
    )
    
    def subject_name(self, obj):
        return obj.subject.name
    subject_name.short_description = 'Matière'
    
    def teacher_name(self, obj):
        return obj.teacher.user.full_name
    teacher_name.short_description = 'Enseignant'
    
    def room_name(self, obj):
        return obj.room.name
    room_name.short_description = 'Salle'
    
    def program_name(self, obj):
        return obj.program.name
    program_name.short_description = 'Programme'
    
    def day_name(self, obj):
        return obj.get_day_of_week_display()
    day_name.short_description = 'Jour'
    
    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"
    time_range.short_description = 'Horaires'
    
    def week_period(self, obj):
        return f"{obj.week_start} → {obj.week_end}"
    week_period.short_description = 'Période'

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('absence_type_name', 'reason_name', 'target_name', 'period', 'is_approved', 'created_by_name')
    list_filter = ('absence_type', 'reason', 'is_approved', 'created_at')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'room__name', 'program__name')
    ordering = ('-start_datetime',)
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Type d\'absence', {
            'fields': ('absence_type', 'reason', 'description')
        }),
        ('Cible', {
            'fields': ('teacher', 'room', 'program')
        }),
        ('Période', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Approbation', {
            'fields': ('is_approved', 'approved_by', 'created_by')
        }),
    )
    
    def absence_type_name(self, obj):
        return obj.get_absence_type_display()
    absence_type_name.short_description = 'Type'
    
    def reason_name(self, obj):
        return obj.get_reason_display()
    reason_name.short_description = 'Raison'
    
    def target_name(self, obj):
        if obj.teacher:
            return f"Enseignant: {obj.teacher.user.full_name}"
        elif obj.room:
            return f"Salle: {obj.room.name}"
        elif obj.program:
            return f"Programme: {obj.program.name}"
        return "Non défini"
    target_name.short_description = 'Cible'
    
    def period(self, obj):
        return f"{obj.start_datetime.strftime('%d/%m/%Y %H:%M')} - {obj.end_datetime.strftime('%d/%m/%Y %H:%M')}"
    period.short_description = 'Période'
    
    def created_by_name(self, obj):
        return obj.created_by.full_name
    created_by_name.short_description = 'Créé par'

@admin.register(MakeupSession)
class MakeupSessionAdmin(admin.ModelAdmin):
    list_display = ('original_schedule_title', 'new_datetime_formatted', 'new_room_name', 'status_name', 'requested_by_name')
    list_filter = ('status', 'created_at')
    search_fields = ('original_schedule__title', 'new_room__name', 'requested_by__first_name', 'requested_by__last_name')
    ordering = ('-created_at',)
    date_hierarchy = 'new_datetime'
    
    fieldsets = (
        ('Séance originale', {
            'fields': ('original_schedule', 'absence')
        }),
        ('Nouveau créneau', {
            'fields': ('new_datetime', 'new_room', 'duration_hours')
        }),
        ('Gestion', {
            'fields': ('status', 'notes', 'requested_by', 'approved_by')
        }),
    )
    
    def original_schedule_title(self, obj):
        return obj.original_schedule.title
    original_schedule_title.short_description = 'Séance originale'
    
    def new_datetime_formatted(self, obj):
        return obj.new_datetime.strftime('%d/%m/%Y %H:%M')
    new_datetime_formatted.short_description = 'Nouveau créneau'
    
    def new_room_name(self, obj):
        return obj.new_room.name
    new_room_name.short_description = 'Nouvelle salle'
    
    def status_name(self, obj):
        return obj.get_status_display()
    status_name.short_description = 'Statut'
    
    def requested_by_name(self, obj):
        return obj.requested_by.full_name
    requested_by_name.short_description = 'Demandé par'
