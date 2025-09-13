from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('verify/', views.verify_token, name='verify_token'),
    path('refresh/', views.refresh_token, name='refresh_token'),
]