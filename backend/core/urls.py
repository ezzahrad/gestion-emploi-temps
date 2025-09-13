from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Departments
    path('departments/', views.DepartmentListCreateView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    
    # Programs
    path('programs/', views.ProgramListCreateView.as_view(), name='program_list'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program_detail'),
    
    # Rooms
    path('rooms/', views.RoomListCreateView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    
    # Subjects
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    
    # Teachers
    path('teachers/', views.TeacherListCreateView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    
    # Students
    path('students/', views.StudentListCreateView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    
    # Teacher Availabilities
    path('teacher-availabilities/', views.TeacherAvailabilityListCreateView.as_view(), name='availability_list'),
    path('teacher-availabilities/<int:pk>/', views.TeacherAvailabilityDetailView.as_view(), name='availability_detail'),
]