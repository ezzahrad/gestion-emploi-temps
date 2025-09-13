from django.urls import path
from . import views, schedule_api_views

urlpatterns = [
    # URLs existantes...
    
    # Nouvelles URLs pour la génération automatique d'emplois du temps
    path('schedule/generate/', schedule_api_views.generate_automatic_schedule, name='generate_schedule'),
    path('schedule/check-conflicts/', schedule_api_views.check_schedule_conflicts, name='check_conflicts'),
    path('schedule/statistics/', schedule_api_views.get_schedule_statistics, name='schedule_statistics'),
]
