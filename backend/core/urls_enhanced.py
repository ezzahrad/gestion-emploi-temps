# urls.py - URLs améliorées pour AppGET
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import ( # type: ignore
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views_enhanced as views

# Configuration du router DRF
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'programs', views.ProgramViewSet, basename='program')
router.register(r'rooms', views.RoomViewSet, basename='room')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'time-slots', views.TimeSlotViewSet, basename='timeslot')
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')
router.register(r'excel-import-logs', views.ExcelImportLogViewSet, basename='excelimportlog')
router.register(r'timetable-generations', views.TimetableGenerationLogViewSet, basename='timetablegeneration')

app_name = 'core'

urlpatterns = [
    # ===== AUTHENTIFICATION JWT =====
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ===== ROUTES DRF =====
    path('api/', include(router.urls)),
    
    # ===== VUES SPÉCIALISÉES =====
    
    # Dashboard et statistiques
    path('api/dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Import/Export
    path('api/import/excel/', views.ExcelImportView.as_view(), name='excel_import'),
    path('api/export/schedule/', views.ExportScheduleView.as_view(), name='schedule_export'),
    
    # Génération automatique d'emploi du temps
    path('api/generate/timetable/', views.TimetableGenerationView.as_view(), name='timetable_generation'),
    
    # ===== VUES FILTRÉES PAR RÔLE =====
    
    # Emplois du temps par rôle
    path('api/my-schedule/', views.PersonalScheduleView.as_view(), name='personal_schedule'),
    path('api/schedule/weekly/', views.WeeklyScheduleView.as_view(), name='weekly_schedule'),
    path('api/schedule/program/<int:program_id>/', views.ProgramScheduleView.as_view(), name='program_schedule'),
    path('api/schedule/teacher/<int:teacher_id>/', views.TeacherScheduleDetailView.as_view(), name='teacher_schedule'),
    path('api/schedule/room/<int:room_id>/', views.RoomScheduleDetailView.as_view(), name='room_schedule'),
    
    # ===== VUES DE RECHERCHE ET FILTRAGE =====
    
    # Recherche globale
    path('api/search/', views.GlobalSearchView.as_view(), name='global_search'),
    
    # Disponibilités
    path('api/availability/teachers/', views.TeacherAvailabilityView.as_view(), name='teacher_availability'),
    path('api/availability/rooms/', views.RoomAvailabilityView.as_view(), name='room_availability'),
    
    # Conflits
    path('api/conflicts/', views.ConflictDetectionView.as_view(), name='conflicts'),
    path('api/conflicts/resolve/', views.ConflictResolutionView.as_view(), name='resolve_conflicts'),
    
    # ===== VUES D'ADMINISTRATION =====
    
    # Statistiques avancées
    path('api/admin/statistics/', views.AdminStatisticsView.as_view(), name='admin_statistics'),
    path('api/admin/reports/', views.AdminReportsView.as_view(), name='admin_reports'),
    
    # Gestion des utilisateurs
    path('api/admin/users/', views.UserManagementView.as_view(), name='user_management'),
    path('api/admin/users/<int:user_id>/role/', views.UserRoleUpdateView.as_view(), name='user_role_update'),
    
    # Maintenance
    path('api/admin/maintenance/cleanup/', views.MaintenanceCleanupView.as_view(), name='maintenance_cleanup'),
    path('api/admin/maintenance/backup/', views.BackupDataView.as_view(), name='backup_data'),
    
    # ===== VUES DE VALIDATION =====
    
    # Validation des données
    path('api/validate/schedule/', views.ScheduleValidationView.as_view(), name='schedule_validation'),
    path('api/validate/capacity/', views.CapacityValidationView.as_view(), name='capacity_validation'),
    
    # ===== API PUBLIQUE (limitée) =====
    
    # Informations publiques (sans authentification)
    path('api/public/departments/', views.PublicDepartmentListView.as_view(), name='public_departments'),
    path('api/public/programs/', views.PublicProgramListView.as_view(), name='public_programs'),
    
    # ===== WEBHOOKS ET NOTIFICATIONS =====
    
    # Notifications en temps réel
    path('api/notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('api/notifications/mark-read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    
    # Webhooks pour intégrations externes
    path('api/webhooks/schedule-update/', views.ScheduleUpdateWebhookView.as_view(), name='schedule_webhook'),
]

# ===== URLS ADDITIONNELLES POUR LES ACTIONS PERSONNALISÉES =====

# URLs pour les actions spécifiques des ViewSets (si nécessaire)
urlpatterns += [
    # Actions sur les départements
    path('api/departments/<int:pk>/statistics/', 
         views.DepartmentViewSet.as_view({'get': 'statistics'}), 
         name='department-statistics'),
    
    # Actions sur les programmes
    path('api/programs/<int:pk>/schedule/', 
         views.ProgramViewSet.as_view({'get': 'schedule'}), 
         name='program-schedule'),
    path('api/programs/<int:pk>/students/', 
         views.ProgramViewSet.as_view({'get': 'students'}), 
         name='program-students'),
    
    # Actions sur les enseignants
    path('api/teachers/<int:pk>/schedule/', 
         views.TeacherViewSet.as_view({'get': 'schedule'}), 
         name='teacher-schedule'),
    path('api/teachers/<int:pk>/workload/', 
         views.TeacherViewSet.as_view({'get': 'workload'}), 
         name='teacher-workload'),
    path('api/teachers/<int:pk>/availability/', 
         views.TeacherViewSet.as_view({'get': 'availability'}), 
         name='teacher-availability'),
    
    # Actions sur les salles
    path('api/rooms/<int:pk>/availability/', 
         views.RoomViewSet.as_view({'get': 'availability'}), 
         name='room-availability'),
    path('api/rooms/<int:pk>/schedule/', 
         views.RoomViewSet.as_view({'get': 'schedule'}), 
         name='room-schedule'),
    path('api/rooms/<int:pk>/utilization/', 
         views.RoomViewSet.as_view({'get': 'utilization'}), 
         name='room-utilization'),
    
    # Actions sur les étudiants
    path('api/students/<int:pk>/schedule/', 
         views.StudentViewSet.as_view({'get': 'schedule'}), 
         name='student-schedule'),
    
    # Actions sur les emplois du temps
    path('api/schedules/weekly/', 
         views.ScheduleViewSet.as_view({'get': 'weekly'}), 
         name='schedules-weekly'),
    path('api/schedules/conflicts/', 
         views.ScheduleViewSet.as_view({'get': 'conflicts'}), 
         name='schedules-conflicts'),
    path('api/schedules/bulk-update/', 
         views.ScheduleViewSet.as_view({'post': 'bulk_update'}), 
         name='schedules-bulk-update'),
]

# ===== PATTERNS DE ROUTES DYNAMIQUES =====

# Routes pour l'export avec paramètres
urlpatterns += [
    path('api/export/schedule/<str:format>/<str:type>/', 
         views.ExportScheduleView.as_view(), 
         name='schedule_export_typed'),
    path('api/export/schedule/<str:format>/<str:type>/<int:target_id>/', 
         views.ExportScheduleView.as_view(), 
         name='schedule_export_targeted'),
]

# Routes pour les rapports
urlpatterns += [
    path('api/reports/usage/', views.UsageReportView.as_view(), name='usage_report'),
    path('api/reports/conflicts/', views.ConflictReportView.as_view(), name='conflict_report'),
    path('api/reports/workload/', views.WorkloadReportView.as_view(), name='workload_report'),
    path('api/reports/utilization/', views.UtilizationReportView.as_view(), name='utilization_report'),
]

# ===== DOCUMENTATION ET MÉTADONNÉES =====

urlpatterns += [
    # Métadonnées de l'API
    path('api/metadata/', views.APIMetadataView.as_view(), name='api_metadata'),
    path('api/version/', views.APIVersionView.as_view(), name='api_version'),
    
    # Statut système
    path('api/health/', views.HealthCheckView.as_view(), name='health_check'),
    path('api/status/', views.SystemStatusView.as_view(), name='system_status'),
]
