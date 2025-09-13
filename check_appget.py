#!/usr/bin/env python3
"""
Script de vérification rapide pour AppGET
Vérifie que tous les composants sont correctement configurés
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
import time

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def check_python():
    """Vérifier la version de Python"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print_status(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
            return True
        else:
            print_status(f"Python {version.major}.{version.minor} - Version 3.8+ requise", "ERROR")
            return False
    except Exception as e:
        print_status(f"Erreur Python: {e}", "ERROR")
        return False

def check_node():
    """Vérifier Node.js"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_status(f"Node.js {version} ✓", "SUCCESS")
            return True
        else:
            print_status("Node.js non trouvé", "ERROR")
            return False
    except Exception as e:
        print_status(f"Erreur Node.js: {e}", "ERROR")
        return False

def check_project_structure():
    """Vérifier la structure du projet"""
    required_files = [
        "backend/manage.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/src/App.tsx",
        "start_appget.bat",
        "start_appget.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print_status("Structure du projet ✓", "SUCCESS")
        return True
    else:
        print_status(f"Fichiers manquants: {', '.join(missing_files)}", "ERROR")
        return False

def check_backend_dependencies():
    """Vérifier les dépendances backend"""
    try:
        # Changer vers le dossier backend
        os.chdir("backend")
        
        # Vérifier si l'environnement virtuel existe
        venv_paths = ["venv", ".venv"]
        venv_exists = any(os.path.exists(path) for path in venv_paths)
        
        if not venv_exists:
            print_status("Environnement virtuel Python non trouvé", "WARNING")
            return False
        
        # Essayer d'importer Django
        try:
            import django
            print_status(f"Django {django.get_version()} ✓", "SUCCESS")
            return True
        except ImportError:
            print_status("Django non installé", "WARNING")
            return False
            
    except Exception as e:
        print_status(f"Erreur dépendances backend: {e}", "ERROR")
        return False
    finally:
        os.chdir("..")

def check_frontend_dependencies():
    """Vérifier les dépendances frontend"""
    try:
        if not os.path.exists("frontend/node_modules"):
            print_status("node_modules non trouvé", "WARNING")
            return False
        
        # Vérifier package.json
        with open("frontend/package.json", "r") as f:
            package_json = json.load(f)
        
        dependencies = package_json.get("dependencies", {})
        required_deps = ["react", "react-dom", "typescript", "vite"]
        
        missing_deps = [dep for dep in required_deps if dep not in dependencies]
        
        if not missing_deps:
            print_status("Dépendances frontend ✓", "SUCCESS")
            return True
        else:
            print_status(f"Dépendances manquantes: {', '.join(missing_deps)}", "WARNING")
            return False
            
    except Exception as e:
        print_status(f"Erreur dépendances frontend: {e}", "ERROR")
        return False

def check_backend_server():
    """Vérifier si le backend est accessible"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code in [200, 404]:  # 404 est OK, ça veut dire que le serveur répond
            print_status("Backend server accessible ✓", "SUCCESS")
            return True
        else:
            print_status(f"Backend server erreur HTTP {response.status_code}", "WARNING")
            return False
    except requests.RequestException:
        print_status("Backend server non accessible", "WARNING")
        return False

def check_frontend_server():
    """Vérifier si le frontend est accessible"""
    try:
        response = requests.get("http://localhost:5173/", timeout=5)
        if response.status_code == 200:
            print_status("Frontend server accessible ✓", "SUCCESS")
            return True
        else:
            print_status(f"Frontend server erreur HTTP {response.status_code}", "WARNING")
            return False
    except requests.RequestException:
        print_status("Frontend server non accessible", "WARNING")
        return False

def check_database():
    """Vérifier la base de données"""
    try:
        db_file = "backend/db.sqlite3"
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            if size > 0:
                print_status(f"Base de données SQLite ({size} bytes) ✓", "SUCCESS")
                return True
            else:
                print_status("Base de données vide", "WARNING")
                return False
        else:
            print_status("Base de données non trouvée", "WARNING")
            return False
    except Exception as e:
        print_status(f"Erreur base de données: {e}", "ERROR")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🔍 VÉRIFICATION APPGET - GESTION EMPLOIS DU TEMPS")
    print("=" * 60)
    print()
    
    checks = [
        ("Python", check_python),
        ("Node.js", check_node),
        ("Structure projet", check_project_structure),
        ("Dépendances backend", check_backend_dependencies),
        ("Dépendances frontend", check_frontend_dependencies),
        ("Base de données", check_database),
        ("Backend server", check_backend_server),
        ("Frontend server", check_frontend_server),
    ]
    
    results = {}
    
    for name, check_func in checks:
        print(f"Vérification {name}...")
        results[name] = check_func()
        print()
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        color = "SUCCESS" if result else "ERROR"
        print_status(f"{status} {name}", color)
    
    print()
    print_status(f"SCORE: {passed}/{total} vérifications réussies", 
                 "SUCCESS" if passed == total else "WARNING")
    
    if passed == total:
        print()
        print_status("🎉 Votre installation AppGET est parfaite !", "SUCCESS")
        print_status("Vous pouvez utiliser start_appget.bat ou start_appget.sh", "INFO")
    else:
        print()
        print_status("⚠️  Certains problèmes détectés", "WARNING")
        print_status("Consultez les messages ci-dessus pour résoudre les problèmes", "INFO")
        
        if not results.get("Backend server") or not results.get("Frontend server"):
            print_status("💡 Conseil: Lancez d'abord les serveurs avec start_appget", "INFO")

if __name__ == "__main__":
    main()