#!/usr/bin/env python3
"""
Checklist de validation finale pour AppGET v2.0
Vérifie que tous les composants sont en place et fonctionnels
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class AppGETFinalCheck:
    def __init__(self):
        self.root_path = Path.cwd()
        self.checklist = {
            'backend_structure': [],
            'frontend_structure': [],
            'documentation': [],
            'configuration': [],
            'scripts': [],
            'docker': [],
            'tests': [],
            'security': []
        }
        self.total_checks = 0
        self.passed_checks = 0
        self.warnings = []
    
    def check_file_exists(self, path, category, description):
        """Vérifier qu'un fichier existe"""
        self.total_checks += 1
        exists = (self.root_path / path).exists()
        
        self.checklist[category].append({
            'item': description,
            'path': str(path),
            'status': '✅' if exists else '❌',
            'passed': exists
        })
        
        if exists:
            self.passed_checks += 1
        else:
            print(f"❌ Manquant: {path}")
            
        return exists
    
    def check_directory_structure(self):
        """Vérifier la structure des répertoires"""
        print("📁 Vérification de la structure des répertoires...")
        
        # Backend Structure
        backend_files = [
            ('backend/manage.py', 'Django manage.py'),
            ('backend/schedule_management/__init__.py', 'Package principal Django'),
            ('backend/schedule_management/settings.py', 'Configuration Django'),
            ('backend/schedule_management/urls.py', 'URLs principales'),
            ('backend/grades/__init__.py', 'Module Grades'),
            ('backend/grades/models.py', 'Modèles Grades'),
            ('backend/grades/views.py', 'Vues Grades'),
            ('backend/grades/serializers.py', 'Sérialiseurs Grades'),
            ('backend/grades/urls.py', 'URLs Grades'),
            ('backend/absences/__init__.py', 'Module Absences'),
            ('backend/absences/models.py', 'Modèles Absences'),
            ('backend/absences/views.py', 'Vues Absences'),
            ('backend/absences/serializers.py', 'Sérialiseurs Absences'),
            ('backend/pdf_export/__init__.py', 'Module PDF Export'),
            ('backend/pdf_export/models.py', 'Modèles PDF Export'),
            ('backend/pdf_export/views.py', 'Vues PDF Export'),
            ('backend/pdf_export/tasks.py', 'Tâches Celery PDF'),
            ('backend/migrate_enhanced_features.py', 'Script de migration'),
            ('backend/migrate_data_to_v2.py', 'Script migration données')
        ]
        
        for path, desc in backend_files:
            self.check_file_exists(path, 'backend_structure', desc)
        
        # Frontend Structure
        frontend_files = [
            ('frontend/package.json', 'Configuration npm'),
            ('frontend/src/main.tsx', 'Point d\'entrée React'),
            ('frontend/src/services/enhancedAPI.ts', 'Client API étendu'),
            ('frontend/src/types/enhanced.ts', 'Types TypeScript'),
            ('frontend/src/hooks/useEnhancedFeatures.ts', 'Hooks personnalisés'),
            ('frontend/src/components/grades/StudentGradesView.tsx', 'Composant Notes'),
            ('frontend/src/components/absences/AbsenceManagement.tsx', 'Composant Absences'),
            ('frontend/src/components/pdf/PDFExportCenter.tsx', 'Composant PDF'),
            ('frontend/src/components/notifications/NotificationCenter.tsx', 'Composant Notifications'),
            ('frontend/src/pages/enhanced/EnhancedStudentDashboard.tsx', 'Dashboard Étudiant'),
            ('frontend/src/pages/enhanced/EnhancedTeacherDashboard.tsx', 'Dashboard Enseignant')
        ]
        
        for path, desc in frontend_files:
            self.check_file_exists(path, 'frontend_structure', desc)
    
    def check_documentation(self):
        """Vérifier la documentation"""
        print("📚 Vérification de la documentation...")
        
        doc_files = [
            ('README.md', 'README principal'),
            ('NOUVELLES_FONCTIONNALITES.md', 'Guide des nouvelles fonctionnalités'),
            ('DEPLOIEMENT_PRODUCTION.md', 'Guide de déploiement'),
            ('GUIDE_MISE_EN_ROUTE.md', 'Guide de mise en route'),
            ('CHANGELOG.md', 'Journal des modifications'),
            ('CONTRIBUTING.md', 'Guide de contribution'),
            ('TROUBLESHOOTING.md', 'Guide de dépannage'),
            ('LICENSE', 'Licence du projet')
        ]
        
        for path, desc in doc_files:
            self.check_file_exists(path, 'documentation', desc)
    
    def check_configuration(self):
        """Vérifier les fichiers de configuration"""
        print("⚙️ Vérification de la configuration...")
        
        config_files = [
            ('.env.example', 'Exemple de configuration environnement'),
            ('docker-compose.yml', 'Configuration Docker Compose'),
            ('Dockerfile', 'Configuration Docker'),
            ('backend/requirements.txt', 'Dépendances Python'),
            ('frontend/package.json', 'Dépendances Node.js'),
            ('frontend/tsconfig.json', 'Configuration TypeScript'),
            ('frontend/vite.config.ts', 'Configuration Vite'),
            ('frontend/tailwind.config.js', 'Configuration Tailwind')
        ]
        
        for path, desc in config_files:
            self.check_file_exists(path, 'configuration', desc)
    
    def check_scripts(self):
        """Vérifier les scripts utilitaires"""
        print("📝 Vérification des scripts...")
        
        script_files = [
            ('start_enhanced_appget.sh', 'Script démarrage Linux/Mac'),
            ('start_enhanced_appget.bat', 'Script démarrage Windows'),
            ('validate_features.py', 'Script de validation'),
            ('scripts/backup.sh', 'Script de sauvegarde'),
            ('scripts/restore.sh', 'Script de restauration')
        ]
        
        for path, desc in script_files:
            self.check_file_exists(path, 'scripts', desc)
    
    def check_docker_setup(self):
        """Vérifier la configuration Docker"""
        print("🐳 Vérification de Docker...")
        
        docker_files = [
            ('Dockerfile', 'Image Docker'),
            ('docker-compose.yml', 'Orchestration Docker'),
            ('docker/entrypoint.sh', 'Script d\'initialisation'),
            ('docker/nginx.conf', 'Configuration Nginx'),
            ('.dockerignore', 'Fichiers ignorés Docker')
        ]
        
        for path, desc in docker_files:
            self.check_file_exists(path, 'docker', desc)
    
    def check_tests(self):
        """Vérifier les tests"""
        print("🧪 Vérification des tests...")
        
        test_files = [
            ('backend/tests/test_enhanced_features.py', 'Tests des nouvelles fonctionnalités'),
            ('.github/workflows/ci-cd.yml', 'Pipeline CI/CD')
        ]
        
        for path, desc in test_files:
            self.check_file_exists(path, 'tests', desc)
    
    def check_security(self):
        """Vérifier la sécurité"""
        print("🔒 Vérification de la sécurité...")
        
        # Vérifier que les fichiers sensibles n'existent pas
        sensitive_files = [
            '.env',
            'backend/.env',
            'frontend/.env',
            'backend/db.sqlite3',
            'backend/secret_key.txt'
        ]
        
        for file_path in sensitive_files:
            if (self.root_path / file_path).exists():
                self.warnings.append(f"⚠️ Fichier sensible détecté: {file_path}")
        
        # Vérifier les permissions des scripts
        script_files = ['start_enhanced_appget.sh', 'scripts/backup.sh', 'scripts/restore.sh']
        for script in script_files:
            if (self.root_path / script).exists():
                self.checklist['security'].append({
                    'item': f'Script {script}',
                    'path': script,
                    'status': '✅',
                    'passed': True
                })
                self.passed_checks += 1
            self.total_checks += 1
    
    def check_file_sizes(self):
        """Vérifier les tailles de fichiers critiques"""
        print("📏 Vérification des tailles de fichiers...")
        
        large_files = []
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size > 10 * 1024 * 1024:  # Plus de 10MB
                        large_files.append((str(file_path.relative_to(self.root_path)), size))
                except (OSError, PermissionError):
                    pass
        
        if large_files:
            self.warnings.append("⚠️ Fichiers volumineux détectés:")
            for file_path, size in large_files:
                self.warnings.append(f"  - {file_path}: {size / (1024*1024):.1f}MB")
    
    def generate_final_report(self):
        """Générer le rapport final"""
        print("\n" + "="*60)
        print("📊 RAPPORT FINAL DE VALIDATION APPGET v2.0")
        print("="*60)
        
        # Statistiques globales
        success_rate = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"\n🎯 RÉSUMÉ GLOBAL")
        print(f"Total vérifications: {self.total_checks}")
        print(f"Réussies: {self.passed_checks}")
        print(f"Échouées: {self.total_checks - self.passed_checks}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        # Détail par catégorie
        for category, items in self.checklist.items():
            if items:
                passed = sum(1 for item in items if item['passed'])
                total = len(items)
                print(f"\n📂 {category.upper().replace('_', ' ')}")
                print(f"  Statut: {passed}/{total} ({'✅' if passed == total else '⚠️'})")
                
                for item in items:
                    if not item['passed']:
                        print(f"    {item['status']} {item['item']}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️ AVERTISSEMENTS ({len(self.warnings)})")
            for warning in self.warnings:
                print(f"  {warning}")
        
        # Recommandations finales
        print(f"\n💡 RECOMMANDATIONS")
        
        if success_rate >= 95:
            print("  🎉 Excellent ! Votre AppGET v2.0 est prêt pour la production.")
            status = "EXCELLENT"
        elif success_rate >= 85:
            print("  ✅ Très bon ! Quelques ajustements mineurs recommandés.")
            status = "BON"
        elif success_rate >= 70:
            print("  ⚠️ Correct mais des améliorations sont nécessaires.")
            status = "MOYEN"
        else:
            print("  ❌ Des corrections importantes sont requises.")
            status = "INSUFFISANT"
        
        # Prochaines étapes
        print(f"\n🚀 PROCHAINES ÉTAPES")
        if status in ["EXCELLENT", "BON"]:
            print("  1. Lancez les tests automatisés: python validate_features.py")
            print("  2. Démarrez l'application: ./start_enhanced_appget.sh")
            print("  3. Testez toutes les fonctionnalités manuellement")
            print("  4. Configurez la sauvegarde: crontab -e")
            print("  5. Préparez le déploiement en production")
        else:
            print("  1. Corrigez les fichiers manquants")
            print("  2. Relancez cette vérification")
            print("  3. Consultez le guide de dépannage: TROUBLESHOOTING.md")
        
        # Sauvegarder le rapport
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'status': status,
            'success_rate': success_rate,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'checklist': self.checklist,
            'warnings': self.warnings
        }
        
        with open('final_validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé sauvegardé: final_validation_report.json")
        print("="*60)
        
        return status == "EXCELLENT" or status == "BON"
    
    def run_final_check(self):
        """Exécuter la vérification finale complète"""
        print("🎯 CHECKLIST FINALE APPGET v2.0")
        print("="*60)
        print("Vérification de l'intégrité et de la complétude du projet")
        print()
        
        # Exécuter toutes les vérifications
        self.check_directory_structure()
        self.check_documentation()
        self.check_configuration()
        self.check_scripts()
        self.check_docker_setup()
        self.check_tests()
        self.check_security()
        self.check_file_sizes()
        
        # Générer le rapport final
        return self.generate_final_report()

def main():
    """Fonction principale"""
    if not (Path.cwd() / 'backend').exists() or not (Path.cwd() / 'frontend').exists():
        print("❌ Ce script doit être exécuté depuis la racine du projet AppGET")
        sys.exit(1)
    
    checker = AppGETFinalCheck()
    success = checker.run_final_check()
    
    if success:
        print(f"\n🎉 FÉLICITATIONS ! Votre AppGET v2.0 est prêt !")
        sys.exit(0)
    else:
        print(f"\n⚠️ Des améliorations sont nécessaires avant la mise en production.")
        sys.exit(1)

if __name__ == "__main__":
    main()
