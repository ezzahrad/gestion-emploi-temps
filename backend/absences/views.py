from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import timedelta, date

from .models import (
    AbsencePolicy, Absence, MakeupSession, 
    AttendanceRecord, StudentAbsenceStatistics
)
from .serializers import (
    AbsencePolicySerializer, AbsenceSerializer, StudentAbsenceSerializer,
    MakeupSessionSerializer, StudentMakeupSessionSerializer,
    AttendanceRecordSerializer, StudentAbsenceStatisticsSerializer,
    BulkAttendanceCreateSerializer, AbsenceReportSerializer
)
from core.permissions import IsTeacherOrAdmin, IsStudentOrTeacher
from schedule.models import Schedule

User = get_user_model()

class AbsencePolicyViewSet(viewsets.ModelViewSet):
    queryset = AbsencePolicy.objects.all()
    serializer_class = AbsencePolicySerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'absence_type', 'status', 'is_makeup_required', 'makeup_completed']
    search_fields = ['student__first_name', 'student__last_name', 'reason']
    ordering_fields = ['absence_date', 'reported_at']
    ordering = ['-absence_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Absence.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres absences
            queryset = queryset.filter(student=user)
        elif user.role == 'teacher':
            # Les enseignants voient les absences des cours qu'ils donnent
            queryset = queryset.filter(schedule__teacher=user.id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return StudentAbsenceSerializer
        return AbsenceSerializer
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            # Les étudiants ne peuvent créer que leurs propres absences
            serializer.save(student=user, reported_by=user)
        else:
            serializer.save(reported_by=user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def approve(self, request, pk=None):
        """Approuver une absence"""
        absence = self.get_object()
        absence.status = 'approved'
        absence.approved_by = request.user
        absence.approved_at = timezone.now()
        absence.save()
        
        return Response({
            'message': 'Absence approuvée avec succès',
            'approved_at': absence.approved_at
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def reject(self, request, pk=None):
        """Rejeter une absence"""
        absence = self.get_object()
        absence.status = 'rejected'
        absence.approved_by = request.user
        absence.approved_at = timezone.now()
        absence.admin_comments = request.data.get('comments', '')
        absence.save()
        
        return Response({
            'message': 'Absence rejetée',
            'rejected_at': absence.approved_at
        })
    
    @action(detail=True, methods=['post'])
    def upload_justification(self, request, pk=None):
        """Télécharger un document justificatif"""
        absence = self.get_object()
        
        # Vérifier que l'utilisateur peut modifier cette absence
        if request.user.role == 'student' and absence.student != request.user:
            return Response(
                {'error': 'Vous ne pouvez pas modifier cette absence'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'justification_document' not in request.FILES:
            return Response(
                {'error': 'Aucun fichier fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        absence.justification_document = request.FILES['justification_document']
        absence.save()
        
        return Response({
            'message': 'Document justificatif téléchargé avec succès',
            'document_url': request.build_absolute_uri(absence.justification_document.url)
        })
    
    @action(detail=False, methods=['get'])
    def my_absences(self, request):
        """Obtenir les absences de l'étudiant connecté"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        absences = Absence.objects.filter(student=request.user).order_by('-absence_date')
        serializer = StudentAbsenceSerializer(absences, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques globales des absences"""
        queryset = self.get_queryset()
        
        stats = {
            'total_absences': queryset.count(),
            'by_type': {},
            'by_status': {},
            'recent_trend': []
        }
        
        # Par type
        for choice in Absence.ABSENCE_TYPE_CHOICES:
            type_code, type_name = choice
            count = queryset.filter(absence_type=type_code).count()
            stats['by_type'][type_code] = {
                'name': type_name,
                'count': count
            }
        
        # Par statut
        for choice in Absence.STATUS_CHOICES:
            status_code, status_name = choice
            count = queryset.filter(status=status_code).count()
            stats['by_status'][status_code] = {
                'name': status_name,
                'count': count
            }
        
        # Tendance des 30 derniers jours
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_absences = queryset.filter(absence_date__gte=thirty_days_ago)
        
        for i in range(30):
            day = thirty_days_ago + timedelta(days=i)
            count = recent_absences.filter(absence_date=day).count()
            stats['recent_trend'].append({
                'date': day.isoformat(),
                'count': count
            })
        
        return Response(stats)

class MakeupSessionViewSet(viewsets.ModelViewSet):
    queryset = MakeupSession.objects.all()
    serializer_class = MakeupSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'teacher', 'room', 'attendance_confirmed']
    search_fields = ['absence__student__first_name', 'absence__student__last_name']
    ordering_fields = ['makeup_date', 'created_at']
    ordering = ['-makeup_date']
    
    def get_queryset(self):
        user = self.request.user
        queryset = MakeupSession.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres sessions
            queryset = queryset.filter(absence__student=user)
        elif user.role == 'teacher':
            # Les enseignants voient leurs sessions ou celles de leurs matières
            queryset = queryset.filter(
                Q(teacher=user) | Q(absence__schedule__teacher=user.id)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.user.role == 'student':
            return StudentMakeupSessionSerializer
        return MakeupSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(scheduled_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def confirm(self, request, pk=None):
        """Confirmer une session de rattrapage"""
        session = self.get_object()
        session.status = 'confirmed'
        session.confirmed_by = request.user
        session.confirmed_at = timezone.now()
        session.save()
        
        return Response({
            'message': 'Session confirmée avec succès',
            'confirmed_at': session.confirmed_at
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marquer une session comme terminée"""
        session = self.get_object()
        
        # Vérifier les permissions
        if (request.user.role == 'teacher' and session.teacher != request.user and 
            session.absence.schedule.teacher != request.user.id):
            return Response(
                {'error': 'Vous ne pouvez pas modifier cette session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attendance_confirmed = request.data.get('attendance_confirmed', True)
        teacher_feedback = request.data.get('teacher_feedback', '')
        makeup_grade = request.data.get('makeup_grade')
        
        session.mark_completed(teacher_feedback, attendance_confirmed)
        
        if makeup_grade:
            session.makeup_grade = makeup_grade
            session.is_successful = float(makeup_grade) >= 10  # Note de passage
            session.save()
        
        return Response({
            'message': 'Session marquée comme terminée',
            'attendance_confirmed': attendance_confirmed
        })
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        """Ajouter un retour sur la session"""
        session = self.get_object()
        user = request.user
        
        if user.role == 'student' and session.absence.student == user:
            session.student_feedback = request.data.get('feedback', '')
        elif user.role == 'teacher' and (session.teacher == user or 
                                       session.absence.schedule.teacher == user.id):
            session.teacher_feedback = request.data.get('feedback', '')
        else:
            return Response(
                {'error': 'Vous ne pouvez pas ajouter de retour à cette session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.save()
        
        return Response({
            'message': 'Retour ajouté avec succès'
        })
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Obtenir les sessions de l'utilisateur connecté"""
        user = request.user
        
        if user.role == 'student':
            sessions = MakeupSession.objects.filter(absence__student=user)
            serializer = StudentMakeupSessionSerializer(sessions, many=True)
        elif user.role == 'teacher':
            sessions = MakeupSession.objects.filter(teacher=user)
            serializer = MakeupSessionSerializer(sessions, many=True)
        else:
            return Response(
                {'error': 'Action non autorisée pour votre rôle'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response(serializer.data)

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'schedule', 'status', 'is_validated']
    search_fields = ['student__first_name', 'student__last_name', 'notes']
    ordering_fields = ['schedule__week_start', 'recorded_at']
    ordering = ['-schedule__week_start']
    
    def get_queryset(self):
        user = self.request.user
        queryset = AttendanceRecord.objects.all()
        
        if user.role == 'teacher':
            # Les enseignants voient les présences de leurs cours
            queryset = queryset.filter(schedule__teacher=user.id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Enregistrer plusieurs présences en une fois"""
        serializer = BulkAttendanceCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def validate_record(self, request, pk=None):
        """Valider un enregistrement de présence"""
        record = self.get_object()
        record.is_validated = True
        record.validated_by = request.user
        record.validated_at = timezone.now()
        record.save()
        
        return Response({
            'message': 'Enregistrement validé avec succès',
            'validated_at': record.validated_at
        })
    
    @action(detail=False, methods=['get'])
    def by_schedule(self, request):
        """Obtenir les présences par planning"""
        schedule_id = request.query_params.get('schedule_id')
        if not schedule_id:
            return Response(
                {'error': 'schedule_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response(
                {'error': 'Planning non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier les permissions
        if (request.user.role == 'teacher' and 
            schedule.teacher != request.user.id):
            return Response(
                {'error': 'Accès non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        records = AttendanceRecord.objects.filter(schedule=schedule)
        serializer = AttendanceRecordSerializer(records, many=True)
        
        return Response({
            'schedule': {
                'id': schedule.id,
                'subject_name': schedule.subject_name,
                'date': schedule.week_start,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time
            },
            'attendance_records': serializer.data
        })

class StudentAbsenceStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentAbsenceStatistics.objects.all()
    serializer_class = StudentAbsenceStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['risk_level', 'is_at_risk']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['absence_rate', 'total_absences', 'last_calculated']
    ordering = ['-absence_rate']
    
    def get_queryset(self):
        user = self.request.user
        queryset = StudentAbsenceStatistics.objects.all()
        
        if user.role == 'student':
            # Les étudiants ne voient que leurs propres statistiques
            queryset = queryset.filter(student=user)
        elif user.role == 'teacher':
            # Les enseignants voient les stats des étudiants de leurs cours
            queryset = queryset.filter(
                student__attendance_records__schedule__teacher=user.id
            ).distinct()
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def recalculate(self, request, pk=None):
        """Recalculer les statistiques d'un étudiant"""
        stats = self.get_object()
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        stats.calculate_statistics(start_date, end_date)
        
        return Response({
            'message': 'Statistiques recalculées avec succès',
            'last_calculated': stats.last_calculated,
            'absence_rate': stats.absence_rate
        })
    
    @action(detail=False, methods=['get'])
    def my_statistics(self, request):
        """Obtenir les statistiques de l'étudiant connecté"""
        if request.user.role != 'student':
            return Response(
                {'error': 'Cette action est réservée aux étudiants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats, created = StudentAbsenceStatistics.objects.get_or_create(
            student=request.user
        )
        
        if created or not stats.last_calculated:
            stats.calculate_statistics()
        
        serializer = StudentAbsenceStatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacherOrAdmin])
    def at_risk_students(self, request):
        """Obtenir la liste des étudiants à risque"""
        at_risk_stats = self.get_queryset().filter(is_at_risk=True)
        serializer = StudentAbsenceStatisticsSerializer(at_risk_stats, many=True)
        
        return Response({
            'count': at_risk_stats.count(),
            'students': serializer.data
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsTeacherOrAdmin])
    def generate_report(self, request):
        """Générer un rapport d'absences"""
        serializer = AbsenceReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Ici, vous pourriez implémenter la génération de rapport
        # Pour l'instant, retournons les données de base
        
        return Response({
            'message': 'Rapport en cours de génération',
            'report_id': f"absence_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            'parameters': serializer.validated_data
        })
