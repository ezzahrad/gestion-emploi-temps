from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GradeScaleViewSet, EvaluationViewSet, GradeViewSet,
    SubjectGradeSummaryViewSet, StudentTranscriptViewSet
)

router = DefaultRouter()
router.register(r'grade-scales', GradeScaleViewSet)
router.register(r'evaluations', EvaluationViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'subject-summaries', SubjectGradeSummaryViewSet)
router.register(r'transcripts', StudentTranscriptViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
