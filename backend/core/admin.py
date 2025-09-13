from django.contrib import admin
from .models import Department, Program, Room, Subject, Teacher, Student, TeacherAvailability

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_name', 'programs_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    def head_name(self, obj):
        return obj.head.full_name if obj.head else 'Aucun'
    head_name.short_description = 'Chef de département'
    
    def programs_count(self, obj):
        return obj.programs.count()
    programs_count.short_description = 'Nombre de programmes'

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level', 'department', 'head_name', 'capacity', 'students_count')
    list_filter = ('level', 'department', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('department', 'level', 'name')
    
    def head_name(self, obj):
        return obj.head.full_name if obj.head else 'Aucun'
    head_name.short_description = 'Chef de programme'
    
    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Nombre d\'étudiants'

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'room_type', 'capacity', 'department', 'is_available')
    list_filter = ('room_type', 'department', 'is_available', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('department', 'room_type', 'name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'subject_type', 'credits', 'hours_per_week', 'semester', 'department')
    list_filter = ('subject_type', 'semester', 'department', 'credits')
    search_fields = ('name', 'code')
    ordering = ('department', 'semester', 'name')
    filter_horizontal = ('program',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'employee_id', 'specialization', 'max_hours_per_week', 'is_available', 'subjects_count')
    list_filter = ('specialization', 'is_available', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'specialization')
    ordering = ('user__last_name', 'user__first_name')
    filter_horizontal = ('subjects',)
    
    def user_name(self, obj):
        return obj.user.full_name
    user_name.short_description = 'Nom'
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Nombre de matières'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'student_id', 'program', 'enrollment_year', 'is_active')
    list_filter = ('program', 'enrollment_year', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'student_id')
    ordering = ('user__last_name', 'user__first_name')
    
    def user_name(self, obj):
        return obj.user.full_name
    user_name.short_description = 'Nom'

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('teacher_name', 'day_name', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'created_at')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name')
    ordering = ('teacher', 'day_of_week', 'start_time')
    
    def teacher_name(self, obj):
        return obj.teacher.user.full_name
    teacher_name.short_description = 'Enseignant'
    
    def day_name(self, obj):
        return obj.get_day_of_week_display()
    day_name.short_description = 'Jour'
