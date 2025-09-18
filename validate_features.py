#!/usr/bin/env python3
"""
Script de validation complète des nouvelles fonctionnalités AppGET
Vérifie que tous les modules sont correctement installés et fonctionnels
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AppGETValidator:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:5173"
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    def log(self, message, level='info'):
        """Logging avec couleurs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == 'success':
            print(f"{Colors.GREEN}✅ [{timestamp}] {message}{Colors.END}")
        elif level == 'error':
            print(f"{Colors.RED}❌ [{timestamp}] {message}{Colors.END}")
        elif level == 'warning':
            print(f"{Colors.YELLOW}⚠️  [{timestamp}] {message}{Colors.END}")
        elif level == 'info':
            print(f"{Colors.BLUE}ℹ️  [{timestamp}] {message}{Colors.END}")
        else:
            print(f"[{timestamp}] {message}")
    
    def test(self, test_name, test_func):
        """Exécuter un test et enregistrer le résultat"""
        self.results['total_tests'] += 1
        self.log(f"Test: {test_name}", 'info')
        
        try:
            result = test_func()
            if result:
                self.results['passed'] += 1
                self.log(f"{test_name} - RÉUSSI", 'success')
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'passed',
                    'message': 'OK'
                })
                return True
            else:
                self.results['failed'] += 1
                self.log(f"{test_name} - ÉCHEC", 'error')
                self.results['tests'].append({
                    'name': test_name,
                    'status': 'failed',
                    'message': 'Test failed'
                })
                return False
        except Exception as e:
            self.results['failed'] += 1
            self.log(f"{test_name} - ERREUR: {str(e)}", 'error')
            self.results['tests'].append({
                'name': test_name,
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def check_file_exists(self, filepath):
        """Vérifier qu'un fichier existe"""
        return os.path.exists(filepath)
    
    def check_directory_structure(self):
        """Vérifier la structure des répertoires"""
        required_dirs = [
            'backend/grades',
            'backend/absences', 
            'backend/pdf_export',
            'frontend/src/components/grades',
            'frontend/src/components/absences',
            'frontend/src/components/pdf',
            'frontend/src/components/notifications'
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                return False
        return True
    
    def check_backend_files(self):
        """Vérifier les fichiers backend essentiels"""
        required_files = [
            'backend/grades/models.py',
            'backend/grades/views.py',
            'backend/grades/urls.py',
            'backend/absences/models.py',
            'backend/absences/views.py',
            'backend/absences/urls.py',
            'backend/pdf_export/models.py',
            'backend/pdf_export/views.py',
            'backend/pdf_export/urls.py',
            'backend/migrate_enhanced_features.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                return False
        return True
    
    def check_frontend_files(self):
        """Vérifier les fichiers frontend essentiels"""
        required_files = [
            'frontend/src/components/grades/StudentGradesView.tsx',
            'frontend/src/components/absences/AbsenceManagement.tsx',
            'frontend/src/components/pdf/PDFExportCenter.tsx',
            'frontend/src/components/notifications/NotificationCenter.tsx',
            'frontend/src/services/enhancedAPI.ts',
            'frontend/src/types/enhanced.ts',
            'frontend/src/hooks/useEnhancedFeatures.ts'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                return False
        return True
    
    def check_backend_server(self):
        """Vérifier que le serveur backend répond"""
        try:
            response = requests.get(f"{self.backend_url}/admin/", timeout=5)
            return response.status_code in [200, 302]  # 302 = redirection vers login
        except:
            return False
    
    def check_api_endpoints(self):
        """Vérifier les endpoints API"""
        endpoints = [
            '/api/grades/',
            '/api/absences/',
            '/api/pdf-export/',
            '/api/notifications/'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                # API doit exister (pas 404)
                if response.status_code == 404:
                    return False
            except:
                return False
        return True
    
    def check_frontend_server(self):
        """Vérifier que le serveur frontend répond"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_docker_compose(self):
        """Vérifier la configuration Docker"""
        return os.path.exists('docker-compose.yml') and os.path.exists('Dockerfile')
    
    def check_documentation(self):
        """Vérifier la documentation"""
        docs = [
            'NOUVELLES_FONCTIONNALITES.md',
            'DEPLOIEMENT_PRODUCTION.md',
            'README.md'
        ]
        
        for doc in docs:
            if not os.path.exists(doc):
                return False
        return True
    
    def check_python_dependencies(self):
        """Vérifier les dépendances Python"""
        try:
            import reportlab
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def check_django_migrations(self):
        """Vérifier les migrations Django"""
        if not os.path.exists('backend/manage.py'):
            return False
        
        try:
            os.chdir('backend')
            result = subprocess.run([
                'python', 'manage.py', 'showmigrations', '--plan'
            ], capture_output=True, text=True, timeout=30)
            os.chdir('..')
            return result.returncode == 0
        except:
            if os.getcwd().endswith('backend'):
                os.chdir('..')
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print(f"{Colors.BOLD}🚀 VALIDATION APPGET - NOUVELLES FONCTIONNALITÉS{Colors.END}")
        print("=" * 60)
        
        # Tests de structure
        self.test("Structure des répertoires", self.check_directory_structure)
        self.test("Fichiers backend", self.check_backend_files)
        self.test("Fichiers frontend", self.check_frontend_files)
        self.test("Configuration Docker", self.check_docker_compose)
        self.test("Documentation", self.check_documentation)
        
        # Tests de dépendances
        self.test("Dépendances Python", self.check_python_dependencies)
        self.test("Migrations Django", self.check_django_migrations)
        
        # Tests de serveurs (optionnels)
        if self.test("Serveur backend", self.check_backend_server):
            self.test("Endpoints API", self.check_api_endpoints)
        
        self.test("Serveur frontend", self.check_frontend_server)
        
        # Résumé final
        self.print_summary()
    
    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 RÉSUMÉ DE LA VALIDATION{Colors.END}")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        
        print(f"Tests exécutés: {total}")
        print(f"{Colors.GREEN}Réussis: {passed}{Colors.END}")
        print(f"{Colors.RED}Échecs: {failed}{Colors.END}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 90:
            self.log("🎉 VALIDATION EXCELLENTE - Application prête pour la production !", 'success')
            status = "EXCELLENT"
        elif success_rate >= 75:
            self.log("✅ VALIDATION BONNE - Quelques améliorations possibles", 'success') 
            status = "BON"
        elif success_rate >= 50:
            self.log("⚠️ VALIDATION MOYENNE - Corrections recommandées", 'warning')
            status = "MOYEN"
        else:
            self.log("❌ VALIDATION INSUFFISANTE - Corrections nécessaires", 'error')
            status = "INSUFFISANT"
        
        # Afficher les détails des échecs
        if failed > 0:
            print(f"\n{Colors.RED}Détails des échecs:{Colors.END}")
            for test in self.results['tests']:
                if test['status'] in ['failed', 'error']:
                    print(f"  ❌ {test['name']}: {test['message']}")
        
        # Générer un rapport JSON
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'success_rate': success_rate,
            'results': self.results
        }
        
        with open('validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Rapport détaillé sauvegardé: validation_report.json")
        
        # Recommandations
        print(f"\n{Colors.BLUE}💡 RECOMMANDATIONS:{Colors.END}")
        
        if success_rate < 100:
            print("1. Corriger les tests en échec avant le déploiement")
        
        if not self.check_backend_server():
            print("2. Démarrer le serveur backend: cd backend && python manage.py runserver")
        
        if not self.check_frontend_server():
            print("3. Démarrer le serveur frontend: cd frontend && npm run dev")
        
        print("4. Exécuter les tests automatisés: python backend/tests/test_enhanced_features.py")
        print("5. Consulter la documentation: NOUVELLES_FONCTIONNALITES.md")
        
        print(f"\n{Colors.BOLD}AppGET est maintenant équipé de fonctionnalités avancées ! 🚀{Colors.END}")

def main():
    """Fonction principale"""
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print(f"{Colors.RED}❌ Ce script doit être exécuté depuis la racine du projet AppGET{Colors.END}")
        sys.exit(1)
    
    validator = AppGETValidator()
    validator.run_all_tests()

if __name__ == "__main__":
    main()
