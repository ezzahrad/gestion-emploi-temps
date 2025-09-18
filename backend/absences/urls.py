from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AbsencePolicyViewSet, AbsenceViewSet, MakeupSessionViewSet,
    AttendanceRecordViewSet, StudentAbsenceStatisticsViewSet
)

router = DefaultRouter()
router.register(r'policies', AbsencePolicyViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'makeup-sessions', MakeupSessionViewSet)
router.register(r'attendance', AttendanceRecordViewSet)
router.register(r'statistics', StudentAbsenceStatisticsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
