from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import GradeScale, Evaluation, Grade, SubjectGradeSummary, StudentTranscript
from .serializers import (
    GradeScaleSerializer, EvaluationSerializer, GradeSerializer,
    StudentGradeSerializer, SubjectGradeSummarySerializer,
    StudentTranscriptSerializer, BulkGradeCreateSerializer
)
from core.permissions import IsTeacherOrAdmin, IsStudentOrTeacher

User = get_user_model()

class GradeScaleViewSet(viewsets.ModelViewSet):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['evaluation_type', 'subject', 'is_published']
    search_fields = ['name', 'subject__name', 'subject__code']
    ordering_fields = ['evaluation_date', 'created_at']
    ordering = ['-evaluation_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Evaluation.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que les évaluations de leurs matières
            queryset = queryset.filter(
                subject__program=user.program,
                is_published=True
            )
        elif user.role == 'teacher':
            # Les enseignants voient les évaluations des matières qu'ils enseignent
            queryset = queryset.filter(
                subject__teachers=user
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def publish(self, request, pk=None):
        """Publier une évaluation"""
        evaluation = self.get_object()
        evaluation.is_published = True
        evaluation.save()
        
        return Response({
            'message': 'Évaluation publiée avec succès',
            'published_at': timezone.now()
        })
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Statistiques d'une évaluation"""
        evaluation = self.get_object()
        grades = evaluation.grades.filter(is_published=True)
        
        if not grades.exists():
            return Response({'message': 'Aucune note disponible'})
        
        stats = {
            'total_grades': grades.count(),
            'average': grades.aggregate(avg=Avg('grade_value'))['avg'],
            'max_grade': evaluation.max_grade,
            'distribution': {
                'A': grades.filter(grade_letter__in=['A+', 'A']).count(),
                'B': grades.filter(grade_letter__in=['B+', 'B']).count(),
                'C': grades.filter(grade_letter__in=['C+', 'C']).count(),
                'D': grades.filter(grade_letter__in=['D+', 'D']).count(),
                'F': grades.filter(grade_letter='F').count(),
            }
        }
        
        return Response(stats)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'evaluation', 'evaluation__subject', 'is_published', 'grade_letter']
    search_fields = ['student__first_name', 'student__last_name', 'evaluation__name']
    ordering_fields = ['grade_value', 'percentage', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Grade.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres notes publiées
            queryset = queryset.filter(student=user, is_published=True)
            
        elif user.role == 'teacher':
            # Les enseignants voient les notes des matières qu'ils enseignent
            queryset = queryset.filter(evaluation__subject__teachers=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return StudentGradeSerializer
        return GradeSerializer
    
    def perform_create(self, serializer):
        serializer.save(graded_by=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def bulk_create(self, request):
        """Créer plusieurs notes en une fois"""
        serializer = BulkGradeCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def publish(self, request, pk=None):
        """Publier une note"""
        grade = self.get_object()
        grade.is_published = True
        grade.published_at = timezone.now()
        grade.save()
        
        return Response({
            'message': 'Note publiée avec succès',
            'published_at': grade.published_at
        })
    
    @action(detail=False, methods=['get'])
    def my_grades(self, request):
        """Obtenir les notes de l'étudiant connecté"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        grades = Grade.objects.filter(
            student=request.user,
            is_published=True
        ).order_by('-evaluation__evaluation_date')
        
        serializer = StudentGradeSerializer(grades, many=True)
        return Response(serializer.data)

class SubjectGradeSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubjectGradeSummary.objects.all()
    serializer_class = SubjectGradeSummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'subject', 'is_validated', 'grade_letter']
    search_fields = ['student__first_name', 'student__last_name', 'subject__name']
    ordering_fields = ['weighted_average', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = SubjectGradeSummary.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres résumés
            queryset = queryset.filter(student=user)
            
        elif user.role == 'teacher':
            # Les enseignants voient les résumés des matières qu'ils enseignent
            queryset = queryset.filter(subject__teachers=user)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def recalculate(self, request, pk=None):
        """Recalculer les moyennes d'un résumé"""
        summary = self.get_object()
        summary.calculate_averages()
        
        return Response({
            'message': 'Moyennes recalculées avec succès',
            'weighted_average': summary.weighted_average
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def validate(self, request, pk=None):
        """Valider un résumé de notes"""
        summary = self.get_object()
        summary.is_validated = True
        summary.validated_by = request.user
        summary.validated_at = timezone.now()
        summary.save()
        
        return Response({
            'message': 'Résumé validé avec succès',
            'validated_at': summary.validated_at
        })
    
    @action(detail=False, methods=['get'])
    def my_summaries(self, request):
        """Obtenir les résumés de l'étudiant connecté"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        summaries = SubjectGradeSummary.objects.filter(
            student=request.user
        ).order_by('subject__name')
        
        serializer = SubjectGradeSummarySerializer(summaries, many=True)
        return Response(serializer.data)

class StudentTranscriptViewSet(viewsets.ModelViewSet):
    queryset = StudentTranscript.objects.all()
    serializer_class = StudentTranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'program', 'semester', 'academic_year', 'is_finalized']
    search_fields = ['student__first_name', 'student__last_name', 'program__name']
    ordering_fields = ['overall_average', 'gpa', 'updated_at']
    ordering = ['-academic_year', '-semester']
    
    def get_queryset(self):
        user = self.request.user
        queryset = StudentTranscript.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres relevés
            queryset = queryset.filter(student=user)
            
        elif user.role == 'teacher':
            # Les enseignants voient les relevés des programmes où ils enseignent
            queryset = queryset.filter(
                program__subjects__teachers=user
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def calculate_gpa(self, request, pk=None):
        """Recalculer le GPA d'un relevé"""
        transcript = self.get_object()
        transcript.calculate_gpa()
        
        return Response({
            'message': 'GPA recalculé avec succès',
            'gpa': transcript.gpa,
            'overall_average': transcript.overall_average
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def finalize(self, request, pk=None):
        """Finaliser un relevé de notes"""
        transcript = self.get_object()
        transcript.is_finalized = True
        transcript.finalized_by = request.user
        transcript.finalized_at = timezone.now()
        transcript.save()
        
        return Response({
            'message': 'Relevé finalisé avec succès',
            'finalized_at': transcript.finalized_at
        })
    
    @action(detail=False, methods=['get'])
    def my_transcripts(self, request):
        """Obtenir les relevés de l'étudiant connecté"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        transcripts = StudentTranscript.objects.filter(
            student=request.user
        ).order_by('-academic_year', '-semester')
        
        serializer = StudentTranscriptSerializer(transcripts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current_transcript(self, request):
        """Obtenir le relevé actuel de l'étudiant"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Trouver le relevé le plus récent
        transcript = StudentTranscript.objects.filter(
            student=request.user
        ).order_by('-academic_year', '-semester').first()
        
        if not transcript:
            return Response(
                {'message': 'Aucun relevé trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentTranscriptSerializer(transcript)
        return Response(serializer.data)
