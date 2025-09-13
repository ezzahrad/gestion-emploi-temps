# Guide de Maintenance et Développement - AppGET

## 📋 Vue d'Ensemble du Projet

**AppGET** est une application complète de gestion des emplois du temps universitaires avec une architecture moderne React/Django optimisée pour les environnements desktop.

## 🏗️ Architecture Technique

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/           # Composants réutilisables
│   │   ├── ui/              # Bibliothèque de composants UI
│   │   │   ├── Button.tsx   # Composants boutons
│   │   │   ├── Card.tsx     # Composants cartes
│   │   │   ├── Modal.tsx    # Modals et dialogs
│   │   │   ├── Table.tsx    # Tables avec tri/filtrage
│   │   │   ├── Form.tsx     # Formulaires avec validation
│   │   │   ├── Loading.tsx  # États de chargement
│   │   │   └── Breadcrumb.tsx # Navigation
│   │   ├── Layout.tsx       # Layout principal responsive
│   │   ├── Login.tsx        # Composant de connexion
│   │   └── ProtectedRoute.tsx # Protection des routes
│   ├── pages/               # Pages de l'application
│   │   ├── Dashboard.tsx    # Tableau de bord générique
│   │   ├── AdminDashboard.tsx # TB administrateur
│   │   ├── TeacherDashboard.tsx # TB enseignant
│   │   ├── ScheduleViewer.tsx # Visualiseur d'emploi du temps
│   │   ├── ConnectionTest.tsx # Tests de connexion
│   │   └── admin/           # Pages d'administration
│   ├── contexts/            # Contextes React
│   │   └── AuthContext.tsx  # Gestion authentification
│   ├── services/            # Services API
│   │   └── api.ts          # Configuration Axios
│   ├── types/               # Types TypeScript
│   └── index.css           # Styles Tailwind optimisés
├── vite.config.ts          # Configuration Vite optimisée
├── tailwind.config.js      # Configuration Tailwind
└── package.json            # Dépendances npm
```

### Backend (Django)
```
backend/
├── authentication/         # App authentification JWT
├── core/                  # Modèles principaux
├── schedule/              # Gestion emplois du temps
├── notifications/         # Système de notifications
├── schedule_management/   # Configuration Django
├── requirements.txt       # Dépendances Python
└── manage.py             # CLI Django
```

## 🎨 Système de Design

### Composants UI Réutilisables

#### Boutons
```tsx
import { Button, IconButton, FloatingActionButton } from '@/components/ui';

// Bouton standard
<Button variant="primary" size="lg" loading={isLoading}>
  Sauvegarder
</Button>

// Bouton avec icône
<Button variant="secondary" icon={<Plus />} iconPosition="left">
  Ajouter
</Button>

// Bouton icône seul
<IconButton icon={<Edit />} tooltip="Modifier" />
```

#### Cartes
```tsx
import { Card, StatCard, ActionCard, CardGrid } from '@/components/ui';

// Carte statistique
<StatCard
  title="Étudiants"
  value={250}
  icon={<Users />}
  color="from-blue-500 to-blue-600"
  trend={{ value: 5, direction: 'up' }}
/>

// Grille de cartes
<CardGrid cols={4} gap="lg">
  {items.map(item => <ActionCard key={item.id} {...item} />)}
</CardGrid>
```

#### Modals
```tsx
import { Modal, ConfirmModal, useModal } from '@/components/ui';

const { isOpen, openModal, closeModal } = useModal();

<ConfirmModal
  isOpen={isOpen}
  onClose={closeModal}
  onConfirm={handleConfirm}
  title="Confirmer la suppression"
  message="Cette action est irréversible"
  variant="danger"
/>
```

#### Tables
```tsx
import { Table } from '@/components/ui';

<Table
  columns={columns}
  data={data}
  pagination={{
    current: page,
    pageSize: 20,
    total: totalItems,
    onChange: handlePageChange
  }}
  selection={{
    selectedRowKeys,
    onChange: handleSelectionChange
  }}
/>
```

#### Formulaires
```tsx
import { Form, Input, Select, TextArea, useForm } from '@/components/ui';

const { values, errors, setValue, validateForm } = useForm({
  name: '',
  email: ''
});

<Form onSubmit={handleSubmit}>
  <Input
    name="name"
    label="Nom"
    required
    validation={{
      required: 'Le nom est requis',
      minLength: { value: 2, message: 'Minimum 2 caractères' }
    }}
  />
</Form>
```

### Couleurs et Thème

```javascript
// tailwind.config.js
colors: {
  primary: {
    500: '#3b82f6',  // Bleu principal
    600: '#2563eb',
    700: '#1d4ed8',
  },
  secondary: {
    500: '#64748b',  // Gris
  },
  success: {
    500: '#22c55e',  // Vert
  },
  warning: {
    500: '#f59e0b',  // Orange
  },
  error: {
    500: '#ef4444',  // Rouge
  }
}
```

## 🔧 Configuration et Personnalisation

### Variables d'Environnement

**Frontend (.env)**
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_URL=http://localhost:5173
VITE_APP_NAME=AppGET
VITE_DEBUG=true
```

**Backend (.env)**
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=appget_db
DB_USER=appget_user
DB_PASSWORD=appget_pass
JWT_SECRET_KEY=jwt-secret
```

### Configuration Responsive

L'application s'adapte automatiquement selon la taille d'écran :

- **Mobile** (<768px) : Sidebar en overlay, navigation simplifiée
- **Tablet** (768px-1024px) : Sidebar rétractable, colonnes adaptées
- **Desktop** (>1024px) : Sidebar étendue, grilles multi-colonnes
- **Large screens** (>1920px) : Espacement optimisé, plus de colonnes

### Personnalisation des Couleurs

```typescript
// Modifier dans tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: {
        // Votre palette de couleurs personnalisée
        500: '#your-color',
      }
    }
  }
}
```

## 🚀 Déploiement et Production

### Build de Production

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
python manage.py collectstatic
python manage.py migrate
```

### Optimisations Appliquées

1. **Code Splitting** : Division automatique des bundles
2. **Tree Shaking** : Suppression du code inutilisé
3. **Image Optimization** : Formats et tailles adaptés
4. **CSS Purging** : Suppression des styles non utilisés
5. **Lazy Loading** : Chargement différé des composants
6. **Service Worker** : Cache des ressources (optionnel)

### Configuration Nginx (Exemple)

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    # Frontend statique
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Fichiers statiques
    location /static/ {
        alias /path/to/backend/static/;
    }
}
```

## 🧪 Tests et Qualité

### Tests Frontend

```bash
# Tests unitaires avec Vitest
npm test

# Tests E2E avec Playwright
npm run test:e2e

# Linting et formatting
npm run lint
npm run format
```

### Tests Backend

```bash
# Tests Django
python manage.py test

# Coverage
coverage run --source='.' manage.py test
coverage report
```

### Outils de Qualité

- **ESLint** : Linting JavaScript/TypeScript
- **Prettier** : Formatage du code
- **TypeScript** : Vérification des types
- **Husky** : Git hooks pour la qualité
- **Django Debug Toolbar** : Debug backend

## 📊 Monitoring et Analytics

### Métriques Frontend

```typescript
// Performance monitoring
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`${entry.name}: ${entry.duration}ms`);
  }
});
observer.observe({ entryTypes: ['measure'] });
```

### Logs Backend

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🔒 Sécurité

### Authentification JWT

```typescript
// Intercepteur Axios pour l'authentification
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('appget_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Bonnes Pratiques Appliquées

1. **Validation côté client et serveur**
2. **Sanitisation des données**
3. **Protection CSRF**
4. **Headers de sécurité**
5. **Chiffrement des mots de passe**
6. **Gestion des permissions granulaires**

## 📱 Responsive Design

### Breakpoints Tailwind

```css
/* Mobile First Approach */
.responsive-grid {
  @apply grid grid-cols-1;          /* Mobile */
  @apply md:grid-cols-2;            /* Tablet */
  @apply lg:grid-cols-3;            /* Desktop */
  @apply xl:grid-cols-4;            /* Large Desktop */
  @apply 2xl:grid-cols-5;           /* XL Desktop */
}
```

### Composants Adaptatifs

```tsx
// Sidebar adaptative
const [sidebarExpanded, setSidebarExpanded] = useState(true);

<div className={`
  transition-all duration-300
  ${sidebarExpanded ? 'w-80' : 'w-16'}
  lg:flex hidden
`}>
```

## 🔄 État et Gestion des Données

### Context API React

```typescript
// AuthContext pour l'authentification globale
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Communication API

```typescript
// Service API centralisé
export const api = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' }
});
```

## 🛠️ Maintenance et Mises à Jour

### Checklist de Maintenance Mensuelle

- [ ] Mettre à jour les dépendances npm
- [ ] Mettre à jour les dépendances Python
- [ ] Vérifier les vulnérabilités de sécurité
- [ ] Nettoyer les logs et fichiers temporaires
- [ ] Sauvegarder la base de données
- [ ] Tester les fonctionnalités critiques
- [ ] Vérifier les performances
- [ ] Mettre à jour la documentation

### Commandes Utiles

```bash
# Vérifier les vulnérabilités
npm audit
pip-audit

# Mettre à jour les dépendances
npm update
pip install -r requirements.txt --upgrade

# Nettoyage
npm run clean
python manage.py clearsessions

# Analyse du bundle
npm run build -- --analyze
```

## 🆘 Dépannage Commun

### Problèmes Fréquents

**Frontend ne se connecte pas au backend :**
```bash
# Vérifier les URLs dans .env
# Vérifier que le backend est démarré
# Vérifier la configuration CORS
```

**Erreurs de build :**
```bash
# Nettoyer le cache
rm -rf node_modules package-lock.json
npm install

# Vérifier TypeScript
npm run type-check
```

**Performance lente :**
```bash
# Analyser le bundle
npm run build -- --analyze

# Profiler React
npm install --save-dev @welldone-software/why-did-you-render
```

## 📞 Support et Ressources

### Contacts

- **Développement** : équipe technique
- **Design** : équipe UX/UI
- **Infrastructure** : équipe DevOps

### Documentation Technique

- [React Documentation](https://react.dev/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs/)

### Outils de Développement

- **IDE recommandé** : VS Code avec extensions React/TypeScript
- **Database management** : DBeaver pour PostgreSQL
- **API testing** : Postman ou Insomnia
- **Design** : Figma pour les maquettes

---

**Version** : 1.0  
**Dernière mise à jour** : Janvier 2025  
**Mainteneur** : Équipe Développement AppGET