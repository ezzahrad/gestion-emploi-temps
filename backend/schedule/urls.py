from django.urls import path
from . import views
from . import optimization_views
from . import import_export_views
from . import generation_views

urlpatterns = [
    # Schedules
    path('schedules/', views.ScheduleListCreateView.as_view(), name='schedule_list'),
    path('schedules/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedules/by-week/', views.get_schedule_by_week, name='schedule_by_week'),
    path('schedules/check-conflicts/', views.check_schedule_conflicts, name='check_conflicts'),
    path('schedules/available-rooms/', views.available_rooms, name='available_rooms'),
    
    # Absences
    path('absences/', views.AbsenceListCreateView.as_view(), name='absence_list'),
    path('absences/<int:pk>/', views.AbsenceDetailView.as_view(), name='absence_detail'),
    
    # Makeup Sessions
    path('makeup-sessions/', views.MakeupSessionListCreateView.as_view(), name='makeup_list'),
    path('makeup-sessions/<int:pk>/', views.MakeupSessionDetailView.as_view(), name='makeup_detail'),
    path('makeup-sessions/<int:pk>/approve/', views.approve_makeup, name='approve_makeup'),
    
    # AI Optimization
    path('optimization/stats/', optimization_views.optimization_stats, name='optimization_stats'),
    path('optimization/optimize/', optimization_views.optimize_schedules, name='optimize_schedules'),
    path('optimization/config/', optimization_views.save_optimization_config, name='save_optimization_config'),
    path('optimization/export/', optimization_views.export_optimization_results, name='export_optimization_results'),
    
    # Import/Export
    path('import/', import_export_views.import_schedules, name='import_schedules'),
    path('import/template/', import_export_views.download_import_template, name='download_import_template'),
    path('export/', import_export_views.export_schedules, name='export_schedules'),
    
    # Génération d'emploi du temps
    path('generation/stats/', generation_views.generation_stats, name='generation_stats'),
]