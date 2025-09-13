# permissions.py - Permissions personnalisées pour AppGET
from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui permet seulement aux administrateurs
    de modifier les objets. Les autres utilisateurs ont un accès en lecture seule.
    """
    
    def has_permission(self, request, view):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Permissions d'écriture seulement pour les administrateurs
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin'


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission qui permet l'accès aux enseignants et administrateurs seulement.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        return user_role in ['admin', 'teacher']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission qui permet à un utilisateur de modifier seulement ses propres objets,
    ou aux administrateurs de tout modifier.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Les administrateurs peuvent tout modifier
        if getattr(request.user, 'role', None) == 'admin':
            return True
        
        # Vérifier si l'objet appartient à l'utilisateur
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission basée sur les rôles avec contrôles granulaires.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Administrateurs ont accès à tout
        if user_role == 'admin':
            return True
        
        # Permissions en lecture pour tous les rôles authentifiés
        if request.method in permissions.SAFE_METHODS:
            return user_role in ['admin', 'department_head', 'program_head', 'teacher', 'student']
        
        # Permissions d'écriture limitées
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Seuls admin, chef département et chef filière peuvent modifier
            return user_role in ['admin', 'department_head', 'program_head']
        
        return False


class StudentViewPermission(permissions.BasePermission):
    """
    Permission pour les vues étudiants - accès en lecture seule à leurs données.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Admin et enseignants peuvent voir toutes les données étudiants
        if user_role in ['admin', 'teacher']:
            return True
        
        # Étudiants peuvent voir leurs propres données seulement
        if user_role == 'student':
            return request.method in permissions.SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)
        
        # Admin et enseignants peuvent voir tout
        if user_role in ['admin', 'teacher']:
            return True
        
        # Étudiants peuvent voir seulement leurs propres données
        if user_role == 'student' and hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class TeacherViewPermission(permissions.BasePermission):
    """
    Permission pour les vues enseignants.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Admin peut tout voir et modifier
        if user_role == 'admin':
            return True
        
        # Enseignants peuvent voir et modifier leurs propres données
        if user_role == 'teacher':
            return True
        
        # Chefs de département peuvent gérer leurs enseignants
        if user_role == 'department_head':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)
        
        # Admin peut tout
        if user_role == 'admin':
            return True
        
        # Enseignants peuvent modifier leurs propres données
        if user_role == 'teacher' and hasattr(obj, 'user'):
            # En lecture seulement pour les autres enseignants
            if request.method in permissions.SAFE_METHODS:
                return True
            # Modification seulement de ses propres données
            return obj.user == request.user
        
        # Chef de département peut gérer les enseignants de son département
        if user_role == 'department_head':
            try:
                from core.models import Teacher
                if isinstance(obj, Teacher):
                    user_departments = request.user.headed_department.all()
                    teacher_departments = obj.departments.all()
                    return any(dept in user_departments for dept in teacher_departments)
            except:
                pass
        
        return False


class ScheduleManagementPermission(permissions.BasePermission):
    """
    Permissions spécifiques pour la gestion des emplois du temps.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return user_role in ['admin', 'department_head', 'program_head', 'teacher', 'student']
        
        # Création/modification pour admin et chefs seulement
        if request.method in ['POST', 'PUT', 'PATCH']:
            return user_role in ['admin', 'department_head', 'program_head']
        
        # Suppression pour admin seulement
        if request.method == 'DELETE':
            return user_role == 'admin'
        
        return False
    
    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)
        
        # Admin peut tout
        if user_role == 'admin':
            return True
        
        # Lecture pour tous les rôles autorisés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Chef de département peut modifier les emplois du temps de son département
        if user_role == 'department_head':
            try:
                user_departments = request.user.headed_department.all()
                if hasattr(obj, 'subject'):
                    return obj.subject.department in user_departments
            except:
                pass
        
        # Chef de filière peut modifier les emplois du temps de sa filière
        if user_role == 'program_head':
            try:
                user_programs = request.user.headed_program.all()
                if hasattr(obj, 'programs'):
                    obj_programs = obj.programs.all()
                    return any(program in user_programs for program in obj_programs)
            except:
                pass
        
        return False


class ImportExportPermission(permissions.BasePermission):
    """
    Permissions pour les fonctionnalités d'import/export.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        action = getattr(view, 'action', None)
        
        # Export autorisé pour tous les rôles
        if action in ['export', 'download'] or request.method == 'GET':
            return user_role in ['admin', 'department_head', 'program_head', 'teacher', 'student']
        
        # Import autorisé seulement pour admin et chefs
        if action in ['import', 'upload'] or request.method == 'POST':
            return user_role in ['admin', 'department_head', 'program_head']
        
        return False


class TimetableGenerationPermission(permissions.BasePermission):
    """
    Permissions pour la génération automatique d'emplois du temps.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        user_role = getattr(request.user, 'role', None)
        
        # Consultation des logs pour tous les niveaux administratifs
        if request.method in permissions.SAFE_METHODS:
            return user_role in ['admin', 'department_head', 'program_head']
        
        # Génération d'emploi du temps seulement pour admin
        if request.method == 'POST':
            return user_role == 'admin'
        
        return False


# Décorateurs utilitaires pour les vues basées sur les fonctions

def admin_required(view_func):
    """Décorateur pour exiger le rôle admin"""
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if getattr(request.user, 'role', None) != 'admin':
            raise PermissionDenied("Accès réservé aux administrateurs")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def teacher_or_admin_required(view_func):
    """Décorateur pour exiger le rôle enseignant ou admin"""
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', None)
        if user_role not in ['admin', 'teacher']:
            raise PermissionDenied("Accès réservé aux enseignants et administrateurs")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def role_required(allowed_roles):
    """Décorateur paramétrable pour exiger certains rôles"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_role = getattr(request.user, 'role', None)
            if user_role not in allowed_roles:
                raise PermissionDenied(f"Accès réservé aux rôles: {', '.join(allowed_roles)}")
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


# Mixins pour les vues basées sur les classes

class AdminRequiredMixin:
    """Mixin pour exiger le rôle admin dans les vues basées sur les classes"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if getattr(request.user, 'role', None) != 'admin':
            raise PermissionDenied("Accès réservé aux administrateurs")
        
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin:
    """Mixin paramétrable pour exiger certains rôles"""
    allowed_roles = []  # À définir dans les classes filles
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', None)
        if user_role not in self.allowed_roles:
            raise PermissionDenied(f"Accès réservé aux rôles: {', '.join(self.allowed_roles)}")
        
        return super().dispatch(request, *args, **kwargs)


class StudentAccessMixin:
    """Mixin pour les vues accessibles aux étudiants"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        user_role = getattr(self.request.user, 'role', None)
        
        # Admin voit tout
        if user_role == 'admin':
            return queryset
        
        # Étudiant voit seulement ses données
        if user_role == 'student':
            try:
                from core.models import Student
                student = Student.objects.get(user=self.request.user)
                
                # Filtrer selon le type de modèle
                if hasattr(queryset.model, 'programs'):
                    return queryset.filter(programs=student.program)
                elif hasattr(queryset.model, 'program'):
                    return queryset.filter(program=student.program)
                elif hasattr(queryset.model, 'user'):
                    return queryset.filter(user=self.request.user)
            except Student.DoesNotExist:
                return queryset.none()
        
        return queryset


class TeacherAccessMixin:
    """Mixin pour les vues accessibles aux enseignants"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        user_role = getattr(self.request.user, 'role', None)
        
        # Admin voit tout
        if user_role == 'admin':
            return queryset
        
        # Enseignant voit ses données
        if user_role == 'teacher':
            try:
                from core.models import Teacher
                teacher = Teacher.objects.get(user=self.request.user)
                
                # Filtrer selon le type de modèle
                if hasattr(queryset.model, 'teacher'):
                    return queryset.filter(teacher=teacher)
                elif hasattr(queryset.model, 'subjects'):
                    return queryset.filter(subjects__in=teacher.subjects.all())
                elif hasattr(queryset.model, 'user'):
                    return queryset.filter(user=self.request.user)
            except Teacher.DoesNotExist:
                return queryset.none()
        
        return queryset
class IsAdminOrDepartmentHead(permissions.BasePermission):
    """
    Permission pour Admin ou Chef de Département
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            getattr(request.user, "role", None) in ["admin", "department_head"]
        )


class IsAdminOrProgramHead(permissions.BasePermission):
    """
    Permission pour Admin ou Responsable de Filière
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            getattr(request.user, "role", None) in ["admin", "program_head"]
        )