# 🎓 AppGET - Système de Gestion d'Emploi du Temps Universitaire

[![Version](https://img.shields.io/badge/Version-2.0-blue.svg)](https://github.com/votre-repo/appget)
[![Django](https://img.shields.io/badge/Django-5.0-success.svg)](https://djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.0-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AppGET** est une plateforme complète de gestion académique pour les universités, offrant une solution moderne et intuitive pour la gestion des emplois du temps, des notes, des absences et bien plus encore.

## 🌟 Aperçu

AppGET simplifie la gestion académique avec une interface moderne et des fonctionnalités avancées adaptées aux besoins des universités d'aujourd'hui.

### ✨ Fonctionnalités Principales

#### 🎓 **Pour les Étudiants**
- 📅 Consultation de l'emploi du temps personnel
- 📊 Suivi des notes en temps réel
- 📋 Gestion des absences avec justificatifs
- 📄 Export des relevés de notes en PDF
- 🔔 Notifications personnalisées

#### 👨‍🏫 **Pour les Enseignants**
- 🗓️ Gestion du planning de cours
- ✏️ Saisie et gestion des notes
- ✅ Prise de présences en temps réel
- 📈 Génération de rapports de classe
- 💬 Communication avec les étudiants

#### 👨‍💼 **Pour les Administrateurs**
- 🏛️ Gestion complète des emplois du temps
- 📊 Analyses et statistiques avancées
- 👥 Gestion des utilisateurs et permissions
- 🔧 Configuration du système
- 📈 Tableaux de bord analytiques

## 🚀 Démarrage Rapide

### 📋 Prérequis

- **Python** 3.8+
- **Node.js** 18+
- **PostgreSQL** 13+ ou SQLite (développement)

### ⚡ Installation Express

```bash
# Télécharger le guide d'installation complet
curl -O https://raw.githubusercontent.com/votre-repo/appget/main/HOW_TO_INSTALL.md

# Installation automatique (recommandé)
./start_enhanced_appget.sh   # Linux/Mac
# ou
./start_enhanced_appget.bat  # Windows
```

**📖 Guide détaillé :** [HOW_TO_INSTALL.md](./HOW_TO_INSTALL.md)

### 🌐 Accès Rapide

Une fois installé, accédez à :

- **🖥️ Interface Étudiants/Enseignants :** http://localhost:5173
- **⚙️ Administration :** http://127.0.0.1:8000/admin
- **🔧 API Documentation :** http://127.0.0.1:8000/api/docs

**Compte de démonstration :**
- Utilisateur : `admin`
- Mot de passe : `admin123`

## 🏗️ Architecture

AppGET utilise une architecture moderne et scalable :

```
🎯 Frontend React/TypeScript ←→ 🔧 API Django REST ←→ 🗄️ Base de données
     ↓                           ↓                      ↓
📱 Interface utilisateur    🚀 Logique métier      📊 Données persistantes
🎨 Design responsive       🔐 Sécurité avancée    🔄 Migrations automatiques
⚡ Performance optimisée   📊 APIs RESTful        💾 Sauvegrades automatiques
```

## 📱 Captures d'Écran

### Dashboard Étudiant
*Interface moderne et intuitive pour consulter emploi du temps, notes et absences*

### Gestion des Notes (Enseignants)
*Saisie rapide et efficace des évaluations avec calcul automatique des moyennes*

### Panneau d'Administration
*Outils complets pour la gestion des utilisateurs et la configuration du système*

## 🛠️ Fonctionnalités Avancées

### 🆕 Nouveautés Version 2.0

| Module | Fonctionnalité | Description |
|--------|----------------|-------------|
| 📊 **Grades** | Système de notation complet | Gestion des évaluations, calcul automatique des moyennes, relevés officiels |
| 📅 **Absences** | Gestion intelligente | Déclaration d'absences, justificatifs numériques, statistiques détaillées |
| 📄 **PDF Export** | Documents professionnels | Export personnalisé emplois du temps, relevés, rapports avec templates |
| 🔔 **Notifications** | Communication temps réel | Alertes personnalisables, notifications push, centres d'alerte |

### 🔧 Technologies Utilisées

#### Backend
- **Django 5.0** - Framework web robuste
- **Django REST Framework** - API RESTful
- **PostgreSQL/SQLite** - Base de données
- **Redis** - Cache et tâches asynchrones
- **Celery** - Traitement en arrière-plan

#### Frontend
- **React 18** - Interface utilisateur
- **TypeScript** - Typage statique
- **Vite** - Bundler moderne et rapide
- **Tailwind CSS** - Framework CSS utilitaire
- **Lucide React** - Icônes modernes

## 📚 Documentation

### 📖 Guides Utilisateur
- **[Guide d'Installation](./HOW_TO_INSTALL.md)** - Installation détaillée pas à pas
- **[Guide des Fonctionnalités](./NOUVELLES_FONCTIONNALITES.md)** - Tour complet des nouvelles fonctionnalités
- **[Guide de Déploiement](./DEPLOIEMENT_PRODUCTION.md)** - Mise en production professionnelle

### 🔧 Documentation Technique
- **[API Documentation](http://localhost:8000/api/docs)** - Swagger UI interactif
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - Détails techniques de l'architecture
- **[Troubleshooting](./TROUBLESHOOTING.md)** - Résolution des problèmes courants

## 🧪 Tests et Qualité

AppGET maintient des standards de qualité élevés :

- ✅ **Tests automatisés** - Suite complète de tests backend et frontend
- 🔍 **Validation continue** - Scripts de vérification automatique
- 📊 **Couverture de code** > 85%
- 🔒 **Audit de sécurité** régulier

```bash
# Lancer les tests
python validate_features.py
```

## 🚀 Déploiement

### 🐳 Docker (Recommandé)
```bash
docker-compose up -d --build
```

### ☁️ Cloud Deploy
AppGET est compatible avec :
- **AWS** (EC2, RDS, S3)
- **Google Cloud Platform**
- **DigitalOcean**
- **Heroku**

**Guide complet :** [DEPLOIEMENT_PRODUCTION.md](./DEPLOIEMENT_PRODUCTION.md)

## 🤝 Contribution

Nous accueillons toutes les contributions ! 

### Comment Contribuer
1. 🍴 **Fork** le projet
2. 🌿 **Créer** une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. 💾 **Commit** vos changements (`git commit -m 'Ajout: nouvelle fonctionnalité'`)
4. 📤 **Push** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. 🔃 **Ouvrir** une Pull Request

### 📝 Standards
- **Code Style** : PEP 8 (Python), ESLint + Prettier (TypeScript)
- **Tests** : Couverture requise pour les nouvelles fonctionnalités
- **Documentation** : Mise à jour obligatoire

## 🆘 Support

### 🐛 Problèmes Techniques
- **[Issues GitHub](../../issues)** - Reporter un bug ou suggérer une amélioration
- **[Discussions](../../discussions)** - Questions et discussions communautaires

### 📞 Contact
- **Email** : support@appget.com
- **Documentation** : [Wiki complet](../../wiki)

## 🎯 Roadmap

### 🔮 Version 2.1 (Q2 2025)
- 📱 Application mobile React Native
- 🤖 IA pour recommandations personnalisées
- 📊 Analytics avancés avec visualisations

### 🌟 Version 2.2 (Q3 2025)
- 🎥 Visioconférence intégrée
- 🌐 Support multilingue complet
- 📋 Système de quiz interactifs

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](./LICENSE) pour plus de détails.

## 🙏 Remerciements

Merci à tous les contributeurs et aux technologies open source qui rendent AppGET possible :

- **Django Community** pour le framework robuste
- **React Team** pour l'interface moderne
- **Tous les contributeurs** qui améliorent continuellement le projet

---

<div align="center">

## 🎓 Transformez votre gestion académique avec AppGET ! 🚀

[![⭐ Star](https://img.shields.io/github/stars/votre-repo/appget?style=social)](../../stargazers)
[![🍴 Fork](https://img.shields.io/github/forks/votre-repo/appget?style=social)](../../network/members)
[![👀 Watch](https://img.shields.io/github/watchers/votre-repo/appget?style=social)](../../watchers)

**Développé avec ❤️ pour l'éducation moderne**

[🚀 Commencer](./HOW_TO_INSTALL.md) • [📚 Documentation](../../wiki) • [💬 Support](../../issues)

</div>