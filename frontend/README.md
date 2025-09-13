# AppGET Frontend 📅

Interface utilisateur moderne pour l'application de Gestion des Emplois du Temps universitaires.

## 🚀 Fonctionnalités

### 🔐 Authentification et Autorisation
- Système d'authentification JWT sécurisé
- Gestion des rôles (Admin, Chef département, Chef filière, Enseignant, Étudiant)
- Permissions granulaires selon les rôles
- Protection des routes sensibles

### 📊 Tableau de bord personnalisé
- Vue d'ensemble adaptée selon le rôle utilisateur
- Statistiques en temps réel
- Actions rapides contextuelles
- Notifications et alertes

### 📅 Gestion des emplois du temps
- Visualisation hebdomadaire et mensuelle
- Vue en grille et en liste
- Filtrage avancé (programme, enseignant, salle, matière)
- Recherche et navigation intuitive

### 📥 Import/Export intelligent
- Import Excel avec validation des données
- Export PDF et Excel personnalisés
- Templates prédéfinis
- Historique des imports avec logs détaillés

### 🤖 Génération automatique
- Algorithme d'optimisation OR-Tools
- Résolution automatique des conflits
- Scores d'efficacité et d'optimisation
- Configuration avancée des contraintes

### 🎨 Interface moderne
- Design responsive avec Tailwind CSS
- Thème sombre et clair (à venir)
- Animations et transitions fluides
- Accessibilité WCAG 2.1 compliant

## 🛠️ Technologies utilisées

- **React 18** - Framework JavaScript moderne
- **TypeScript** - Typage statique pour plus de robustesse
- **Vite** - Build tool rapide et moderne
- **Tailwind CSS** - Framework CSS utilitaire
- **React Router** - Routage côté client
- **React Hot Toast** - Notifications élégantes
- **Lucide React** - Icônes SVG optimisées
- **Date-fns** - Manipulation des dates
- **Axios** - Client HTTP (à ajouter si nécessaire)

## 📋 Prérequis

- Node.js 18.0+ 
- npm 9.0+ ou Yarn 1.22+
- Backend Django en fonctionnement

## 🚀 Installation

1. **Cloner le repository**
```bash
git clone https://github.com/university/appget-frontend.git
cd appget-frontend
```

2. **Installer les dépendances**
```bash
npm install
# ou
yarn install
```

3. **Configuration de l'environnement**
```bash
cp .env.example .env
```

Modifier le fichier `.env` avec vos paramètres :
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=AppGET
VITE_UNIVERSITY_NAME="Votre Université"
```

4. **Lancer en mode développement**
```bash
npm run dev
# ou
yarn dev
```

L'application sera accessible sur `http://localhost:3000`

## 🏗️ Build de production

```bash
# Build optimisé
npm run build

# Preview du build
npm run preview

# Vérification des types
npm run type-check

# Linting
npm run lint
```

## 📁 Structure du projet

```
src/
├── components/          # Composants réutilisables
│   ├── Layout.tsx      # Layout principal avec navigation
│   ├── Login.tsx       # Composant de connexion
│   └── ProtectedRoute.tsx # Protection des routes
├── contexts/           # Contextes React
│   └── AuthContext.tsx # Contexte d'authentification
├── pages/             # Pages de l'application
│   ├── Dashboard.tsx  # Tableau de bord principal
│   ├── ScheduleViewer.tsx # Visualisation emploi du temps
│   └── admin/         # Pages administrateur
│       ├── AdminImportExcel.tsx
│       └── AdminTimetableGeneration.tsx
├── utils/             # Utilitaires
├── types/             # Types TypeScript
├── assets/            # Assets statiques
├── App.tsx            # Composant racine
├── main.tsx           # Point d'entrée
└── index.css          # Styles principaux
```

## 🎭 Rôles et permissions

### 🔴 Administrateur
- Gestion complète du système
- Import/export de données
- Génération automatique d'emplois du temps
- Gestion des utilisateurs
- Accès aux statistiques avancées

### 🔵 Chef de département
- Gestion des enseignants de son département
- Gestion des salles et matières
- Validation des emplois du temps
- Statistiques départementales

### 🟢 Chef de filière
- Gestion des étudiants de sa filière
- Planification des cours
- Suivi des programmes
- Statistiques de filière

### 🟣 Enseignant
- Consultation de son emploi du temps
- Gestion de ses disponibilités
- Vue sur ses étudiants
- Export de ses données personnelles

### 🟡 Étudiant
- Consultation de son emploi du temps
- Informations sur son programme
- Export de son planning
- Vue en lecture seule

## 🔒 Sécurité

- **Authentification JWT** avec refresh tokens
- **Protection CSRF** sur toutes les requêtes
- **Validation côté client** et serveur
- **Routes protégées** selon les rôles
- **Headers de sécurité** configurés
- **Chiffrement des données sensibles**

## 🎨 Personnalisation

### Thèmes
Le système de thèmes utilise les CSS custom properties :

```css
:root {
  --color-primary: #2563eb;
  --color-secondary: #64748b;
  /* ... */
}
```

### Composants
Tous les composants utilisent Tailwind CSS avec des classes utilitaires personnalisées définies dans `index.css`.

## 📱 Responsive Design

L'interface s'adapte automatiquement à tous les écrans :

- **Mobile** : Navigation en drawer, layout adaptatif
- **Tablet** : Interface hybride optimisée
- **Desktop** : Sidebar fixe, multi-colonnes
- **Print** : Styles d'impression optimisés

## ⚡ Performances

- **Code splitting** automatique par routes
- **Lazy loading** des composants lourds
- **Mise en cache intelligente** des données
- **Bundle analysis** avec Vite
- **Tree shaking** pour réduire la taille
- **Compression gzip** en production

## 🧪 Tests (à implémenter)

```bash
# Tests unitaires
npm run test

# Tests d'intégration
npm run test:integration

# Tests E2E
npm run test:e2e

# Coverage
npm run test:coverage
```

## 📊 Monitoring (à implémenter)

- **Sentry** pour le tracking d'erreurs
- **Analytics** pour l'usage utilisateur
- **Performance monitoring** avec Web Vitals
- **A/B Testing** pour l'optimisation UX

## 🌐 Internationalisation (à implémenter)

Support prévu pour :
- Français (par défaut)
- Arabe
- Anglais

## 📋 Roadmap

### v1.1 (Q2 2024)
- [ ] Mode sombre complet
- [ ] Notifications push
- [ ] Mode hors ligne (PWA)
- [ ] Tests automatisés

### v1.2 (Q3 2024)
- [ ] Internationalisation
- [ ] Thèmes personnalisables
- [ ] Module de reporting avancé
- [ ] API GraphQL

### v1.3 (Q4 2024)
- [ ] Mobile app (React Native)
- [ ] Intégration calendriers externes
- [ ] IA pour suggestions d'optimisation
- [ ] Workflow d'approbation

## 🐛 Signaler un bug

1. Vérifier que le bug n'est pas déjà signalé
2. Créer une issue avec le template fourni
3. Inclure les étapes de reproduction
4. Joindre les logs et captures d'écran

## 🤝 Contribuer

1. Fork du projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit des changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📞 Support

- 📧 **Email** : dev@university.edu
- 📱 **Téléphone** : +212 528 xx xx xx
- 💬 **Chat** : Support intégré dans l'app
- 📚 **Documentation** : [docs.appget.university.edu](https://docs.appget.university.edu)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Équipe de développement

- **Lead Developer** : [Nom]
- **Frontend Team** : [Équipe]
- **UX/UI Designer** : [Designer]
- **DevOps** : [DevOps]

## 🙏 Remerciements

- Université Ibn Zohr pour le soutien
- Équipe pédagogique pour les retours
- Communauté open source pour les outils
- Étudiants et enseignants pour les tests

---

**Made with ❤️ for education in Morocco 🇲🇦**
