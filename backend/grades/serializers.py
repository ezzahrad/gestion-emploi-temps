from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import GradeScale, Evaluation, Grade, SubjectGradeSummary, StudentTranscript
from core.models import Subject

User = get_user_model()

class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    grades_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Evaluation
        fields = [
            'id', 'name', 'evaluation_type', 'subject', 'subject_name', 
            'subject_code', 'max_grade', 'coefficient', 'evaluation_date',
            'description', 'is_published', 'created_by', 'created_by_name',
            'grades_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_grades_count(self, obj):
        return obj.grades.count()

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    evaluation_name = serializers.CharField(source='evaluation.name', read_only=True)
    subject_name = serializers.CharField(source='evaluation.subject.name', read_only=True)
    subject_code = serializers.CharField(source='evaluation.subject.code', read_only=True)
    max_grade = serializers.DecimalField(source='evaluation.max_grade', read_only=True, max_digits=5, decimal_places=2)
    coefficient = serializers.DecimalField(source='evaluation.coefficient', read_only=True, max_digits=3, decimal_places=2)
    evaluation_date = serializers.DateTimeField(source='evaluation.evaluation_date', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'evaluation', 'evaluation_name',
            'subject_name', 'subject_code', 'grade_value', 'max_grade',
            'percentage', 'grade_letter', 'coefficient', 'evaluation_date',
            'comments', 'is_published', 'published_at', 'graded_by',
            'graded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['percentage', 'grade_letter', 'graded_by', 'published_at', 'created_at', 'updated_at']

class StudentGradeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les notes vues par l'étudiant (données limitées)"""
    evaluation_name = serializers.CharField(source='evaluation.name', read_only=True)
    evaluation_type = serializers.CharField(source='evaluation.evaluation_type', read_only=True)
    subject_name = serializers.CharField(source='evaluation.subject.name', read_only=True)
    subject_code = serializers.CharField(source='evaluation.subject.code', read_only=True)
    max_grade = serializers.DecimalField(source='evaluation.max_grade', read_only=True, max_digits=5, decimal_places=2)
    coefficient = serializers.DecimalField(source='evaluation.coefficient', read_only=True, max_digits=3, decimal_places=2)
    evaluation_date = serializers.DateTimeField(source='evaluation.evaluation_date', read_only=True)
    
    class Meta:
        model = Grade
        fields = [
            'id', 'evaluation_name', 'evaluation_type', 'subject_name',
            'subject_code', 'grade_value', 'max_grade', 'percentage',
            'grade_letter', 'coefficient', 'evaluation_date', 'comments',
            'published_at'
        ]

class SubjectGradeSummarySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_credits = serializers.IntegerField(source='subject.credits', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.full_name', read_only=True)
    
    # Ajouter les notes détaillées
    grades = StudentGradeSerializer(source='student.grades', many=True, read_only=True)
    
    class Meta:
        model = SubjectGradeSummary
        fields = [
            'id', 'student', 'student_name', 'subject', 'subject_name',
            'subject_code', 'subject_credits', 'average_grade', 'weighted_average',
            'grade_letter', 'total_evaluations', 'published_evaluations',
            'total_coefficient', 'is_validated', 'validated_by',
            'validated_by_name', 'validated_at', 'grades', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'average_grade', 'weighted_average', 'grade_letter',
            'total_evaluations', 'published_evaluations', 'total_coefficient',
            'validated_by', 'validated_at', 'created_at', 'updated_at'
        ]

class StudentTranscriptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id = serializers.CharField(source='student.username', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    level = serializers.CharField(source='program.level', read_only=True)
    department_name = serializers.CharField(source='program.department.name', read_only=True)
    finalized_by_name = serializers.CharField(source='finalized_by.full_name', read_only=True)
    
    # Ajouter les résumés par matière
    subjects = SubjectGradeSummarySerializer(source='student.subject_summaries', many=True, read_only=True)
    
    class Meta:
        model = StudentTranscript
        fields = [
            'id', 'student', 'student_name', 'student_id', 'program',
            'program_name', 'program_code', 'level', 'department_name',
            'semester', 'academic_year', 'overall_average', 'gpa',
            'grade_letter', 'total_credits', 'acquired_credits', 'rank',
            'total_students', 'is_finalized', 'finalized_by', 'finalized_by_name',
            'finalized_at', 'subjects', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'overall_average', 'gpa', 'grade_letter', 'total_credits',
            'acquired_credits', 'rank', 'total_students', 'finalized_by',
            'finalized_at', 'created_at', 'updated_at'
        ]

class BulkGradeCreateSerializer(serializers.Serializer):
    """Sérialiseur pour la création en masse de notes"""
    evaluation = serializers.IntegerField()
    grades = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    def validate_evaluation(self, value):
        try:
            return Evaluation.objects.get(id=value)
        except Evaluation.DoesNotExist:
            raise serializers.ValidationError("Évaluation non trouvée")
    
    def validate_grades(self, value):
        """Valider le format des notes"""
        for grade_data in value:
            if 'student_id' not in grade_data or 'grade_value' not in grade_data:
                raise serializers.ValidationError(
                    "Chaque note doit contenir 'student_id' et 'grade_value'"
                )
            
            try:
                float(grade_data['grade_value'])
            except ValueError:
                raise serializers.ValidationError(
                    f"Valeur de note invalide: {grade_data['grade_value']}"
                )
        
        return value
    
    def create(self, validated_data):
        evaluation = validated_data['evaluation']
        grades_data = validated_data['grades']
        user = self.context['request'].user
        
        grades_to_create = []
        errors = []
        
        for grade_data in grades_data:
            try:
                student = User.objects.get(
                    id=grade_data['student_id'],
                    role='student'
                )
                
                grade_value = float(grade_data['grade_value'])
                
                # Vérifier que la note n'existe pas déjà
                if Grade.objects.filter(student=student, evaluation=evaluation).exists():
                    errors.append(f"Note déjà existante pour {student.full_name}")
                    continue
                
                grades_to_create.append(
                    Grade(
                        student=student,
                        evaluation=evaluation,
                        grade_value=grade_value,
                        comments=grade_data.get('comments', ''),
                        graded_by=user
                    )
                )
                
            except User.DoesNotExist:
                errors.append(f"Étudiant non trouvé: {grade_data['student_id']}")
            except ValueError:
                errors.append(f"Valeur de note invalide: {grade_data['grade_value']}")
        
        if errors:
            raise serializers.ValidationError({'errors': errors})
        
        # Créer toutes les notes en une fois
        created_grades = Grade.objects.bulk_create(grades_to_create)
        
        return {
            'created_count': len(created_grades),
            'evaluation': evaluation.id,
            'grades': GradeSerializer(created_grades, many=True).data
        }
