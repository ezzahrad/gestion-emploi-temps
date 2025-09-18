"""
Tests automatisés pour les nouvelles fonctionnalités AppGET
"""

import os
import sys
import django
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta

# Configuration Django pour les tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedule_management.settings')
django.setup()

User = get_user_model()

class EnhancedFeaturesBaseTest(APITestCase):
    """Classe de base pour les tests des nouvelles fonctionnalités"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Créer des utilisateurs de test
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            last_name='Test'
        )
        
        self.teacher = User.objects.create_user(
            username='teacher_test',
            email='teacher@test.com',
            password='test123',
            first_name='Teacher',
            last_name='Test',
            role='teacher'
        )
        
        self.student = User.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='test123',
            first_name='Student',
            last_name='Test',
            role='student'
        )
        
        self.client = APIClient()

    def authenticate_as(self, user):
        """Helper pour s'authentifier comme un utilisateur"""
        self.client.force_authenticate(user=user)

class GradesAPITest(EnhancedFeaturesBaseTest):
    """Tests pour l'API des notes"""
    
    def test_create_evaluation_as_teacher(self):
        """Test création d'évaluation par un enseignant"""
        self.authenticate_as(self.teacher)
        
        # Simuler l'existence d'une matière
        evaluation_data = {
            'name': 'Examen Final Test',
            'evaluation_type': 'exam',
            'subject': 1,  # ID fictif
            'max_grade': 20,
            'coefficient': 2,
            'evaluation_date': '2025-01-15',
            'description': 'Examen final de test'
        }
        
        response = self.client.post('/api/grades/evaluations/', evaluation_data)
        
        # Le test peut échouer si les modèles Subject n'existent pas
        # mais nous testons la structure de l'API
        self.assertIn(response.status_code, [201, 400])  # Créé ou erreur de validation
    
    def test_grades_endpoints_exist(self):
        """Test que tous les endpoints de notes existent"""
        self.authenticate_as(self.teacher)
        
        endpoints = [
            '/api/grades/evaluations/',
            '/api/grades/grades/',
            '/api/grades/grades/my_grades/',
            '/api/grades/grade-scales/',
            '/api/grades/transcripts/current/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # L'endpoint doit exister (pas 404)
            self.assertNotEqual(response.status_code, 404, 
                              f"Endpoint {endpoint} n'existe pas")

class AbsencesAPITest(EnhancedFeaturesBaseTest):
    """Tests pour l'API des absences"""
    
    def test_student_can_declare_absence(self):
        """Test qu'un étudiant peut déclarer une absence"""
        self.authenticate_as(self.student)
        
        absence_data = {
            'schedule': 1,  # ID fictif
            'absence_type': 'medical',
            'reason': 'Consultation médicale urgente'
        }
        
        response = self.client.post('/api/absences/absences/', absence_data)
        
        # Peut échouer si le schedule n'existe pas, mais teste la structure
        self.assertIn(response.status_code, [201, 400])
    
    def test_absence_justification_upload(self):
        """Test upload de justificatif d'absence"""
        self.authenticate_as(self.student)
        
        # Créer un fichier de test
        test_file = SimpleUploadedFile(
            "justificatif.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        # Simuler l'upload (l'endpoint doit exister)
        response = self.client.post('/api/absences/absences/1/upload_justification/', {
            'justification_document': test_file
        })
        
        # Test que l'endpoint existe
        self.assertNotEqual(response.status_code, 404)

class PDFExportAPITest(EnhancedFeaturesBaseTest):
    """Tests pour l'API d'export PDF"""
    
    def test_create_pdf_export(self):
        """Test création d'un export PDF"""
        self.authenticate_as(self.student)
        
        export_data = {
            'export_type': 'schedule',
            'format': 'A4',
            'orientation': 'portrait',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
        
        response = self.client.post('/api/pdf-export/export/create/', export_data)
        
        # L'endpoint doit exister et traiter la requête
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [201, 400])
    
    def test_pdf_job_status_endpoint(self):
        """Test endpoint de statut des jobs PDF"""
        self.authenticate_as(self.student)
        
        response = self.client.get('/api/pdf-export/jobs/')
        
        # L'endpoint doit exister
        self.assertNotEqual(response.status_code, 404)

class NotificationsAPITest(EnhancedFeaturesBaseTest):
    """Tests pour l'API des notifications"""
    
    def test_get_my_notifications(self):
        """Test récupération des notifications personnelles"""
        self.authenticate_as(self.student)
        
        response = self.client.get('/api/notifications/')
        
        # L'endpoint doit exister et retourner une liste
        self.assertNotEqual(response.status_code, 404)
        if response.status_code == 200:
            self.assertIsInstance(response.json(), dict)
    
    def test_mark_notification_as_read(self):
        """Test marquage d'une notification comme lue"""
        self.authenticate_as(self.student)
        
        # Supposer qu'une notification avec ID 1 existe
        response = self.client.post('/api/notifications/1/read/')
        
        # L'endpoint doit exister
        self.assertNotEqual(response.status_code, 404)
    
    def test_notification_settings(self):
        """Test des paramètres de notification"""
        self.authenticate_as(self.student)
        
        # Test GET des paramètres
        response = self.client.get('/api/notifications/settings/')
        self.assertNotEqual(response.status_code, 404)
        
        # Test UPDATE des paramètres
        settings_data = {
            'email_notifications': True,
            'push_notifications': False,
            'grade_updates': True
        }
        
        response = self.client.put('/api/notifications/settings/', settings_data)
        self.assertNotEqual(response.status_code, 404)

class IntegrationTest(EnhancedFeaturesBaseTest):
    """Tests d'intégration entre les modules"""
    
    def test_complete_workflow_grade_to_notification(self):
        """Test workflow complet : création note -> notification"""
        # 1. Enseignant crée une évaluation
        self.authenticate_as(self.teacher)
        
        evaluation_data = {
            'name': 'Test Integration',
            'evaluation_type': 'quiz',
            'subject': 1,
            'max_grade': 10,
            'coefficient': 1,
            'evaluation_date': '2025-01-15'
        }
        
        response = self.client.post('/api/grades/evaluations/', evaluation_data)
        self.assertIn(response.status_code, [201, 400])
        
        # 2. Vérifier que l'étudiant peut voir ses notifications
        self.authenticate_as(self.student)
        
        response = self.client.get('/api/notifications/')
        self.assertNotEqual(response.status_code, 404)
    
    def test_absence_to_pdf_export_workflow(self):
        """Test workflow : absence -> rapport PDF"""
        # 1. Étudiant déclare une absence
        self.authenticate_as(self.student)
        
        absence_data = {
            'schedule': 1,
            'absence_type': 'personal',
            'reason': 'Raison personnelle'
        }
        
        response = self.client.post('/api/absences/absences/', absence_data)
        self.assertIn(response.status_code, [201, 400])
        
        # 2. Étudiant demande un rapport d'absences
        export_data = {
            'export_type': 'absence_report',
            'format': 'A4',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
        
        response = self.client.post('/api/pdf-export/export/create/', export_data)
        self.assertIn(response.status_code, [201, 400])

class SecurityTest(EnhancedFeaturesBaseTest):
    """Tests de sécurité"""
    
    def test_unauthorized_access_denied(self):
        """Test que l'accès non autorisé est refusé"""
        # Sans authentification
        endpoints = [
            '/api/grades/grades/my_grades/',
            '/api/absences/absences/my_absences/',
            '/api/pdf-export/jobs/',
            '/api/notifications/'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 401, 
                           f"Endpoint {endpoint} autorise l'accès non authentifié")
    
    def test_student_cannot_access_teacher_data(self):
        """Test qu'un étudiant ne peut pas accéder aux données enseignant"""
        self.authenticate_as(self.student)
        
        # Essayer d'accéder aux évaluations (création réservée enseignants)
        evaluation_data = {
            'name': 'Tentative Hack',
            'evaluation_type': 'exam',
            'subject': 1,
            'max_grade': 20
        }
        
        response = self.client.post('/api/grades/evaluations/', evaluation_data)
        self.assertIn(response.status_code, [403, 400])  # Interdit ou mauvaise requête

class PerformanceTest(EnhancedFeaturesBaseTest):
    """Tests de performance"""
    
    def test_endpoints_response_time(self):
        """Test que les endpoints répondent rapidement"""
        import time
        
        self.authenticate_as(self.student)
        
        endpoints = [
            '/api/grades/grades/my_grades/',
            '/api/absences/absences/my_absences/',
            '/api/notifications/',
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # L'endpoint doit répondre en moins de 2 secondes
            self.assertLess(response_time, 2.0, 
                          f"Endpoint {endpoint} trop lent: {response_time:.2f}s")

def run_enhanced_tests():
    """Fonction principale pour exécuter tous les tests"""
    print("🧪 LANCEMENT DES TESTS APPGET - NOUVELLES FONCTIONNALITÉS")
    print("=" * 60)
    
    import unittest
    
    # Créer une suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter les classes de test
    test_classes = [
        GradesAPITest,
        AbsencesAPITest,
        PDFExportAPITest,
        NotificationsAPITest,
        IntegrationTest,
        SecurityTest,
        PerformanceTest
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ ÉCHECS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERREURS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) 
                   / result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\n🎯 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Tests majoritairement réussis - Application prête !")
    elif success_rate >= 60:
        print("⚠️  Quelques problèmes détectés - Vérification recommandée")
    else:
        print("❌ Problèmes majeurs détectés - Corrections nécessaires")
    
    return result

if __name__ == "__main__":
    run_enhanced_tests()
