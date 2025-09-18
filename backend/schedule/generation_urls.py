from django.urls import path
from . import generation_views

urlpatterns = [
    path('timetable/', generation_views.generate_timetable, name='generate_timetable'),
    path('stats/', generation_views.generation_stats, name='generation_stats'),
]
