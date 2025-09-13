from django.urls import path
from . import views

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
]