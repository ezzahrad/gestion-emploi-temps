# 🤝 Guide de Contribution - AppGET

Merci de votre intérêt pour contribuer à **AppGET** ! Ce guide vous explique comment participer efficacement au développement de cette plateforme de gestion académique.

---

## 📋 **Table des Matières**

1. [Code de Conduite](#-code-de-conduite)
2. [Comment Contribuer](#-comment-contribuer)
3. [Configuration de l'Environnement](#️-configuration-de-lenvironnement)
4. [Standards de Code](#-standards-de-code)
5. [Process de Développement](#-process-de-développement)
6. [Tests](#-tests)
7. [Documentation](#-documentation)
8. [Pull Requests](#-pull-requests)
9. [Signalement de Bugs](#-signalement-de-bugs)
10. [Support](#-support)

---

## 📜 **Code de Conduite**

### **Notre Engagement**
En participant à ce projet, nous nous engageons à faire de la participation une expérience exempte de harcèlement pour tout le monde, quel que soit l'âge, la taille corporelle, le handicap visible ou invisible, l'ethnicité, les caractéristiques sexuelles, l'identité et l'expression de genre, le niveau d'expérience, l'éducation, le statut socio-économique, la nationalité, l'apparence personnelle, la race, la religion, ou l'identité et l'orientation sexuelle.

### **Standards Attendus**
- **Bienveillance** et respect envers tous les participants
- **Constructivité** dans les critiques et suggestions
- **Professionnalisme** dans toutes les interactions
- **Entraide** et partage de connaissances
- **Respect** des différences d'opinion et d'approche

### **Comportements Inacceptables**
- Harcèlement sous toute forme
- Attaques personnelles ou politiques
- Trolling, commentaires insultants
- Publication d'informations privées sans autorisation
- Tout comportement inapproprié en contexte professionnel

---

## 🚀 **Comment Contribuer**

### **Types de Contributions**

#### 🐛 **Correction de Bugs**
- Consultez les [issues existantes](../../issues)
- Reproduisez le bug localement
- Créez une branche pour votre correction
- Soumettez une Pull Request avec tests

#### ✨ **Nouvelles Fonctionnalités**
- Discutez d'abord dans une issue
- Suivez l'architecture existante
- Documentez votre fonctionnalité
- Incluez des tests complets

#### 📚 **Documentation**
- Améliorez la clarté et l'exactitude
- Ajoutez des exemples pratiques
- Traduisez en d'autres langues
- Créez des tutoriels

#### 🧪 **Tests**
- Augmentez la couverture de tests
- Créez des tests d'intégration
- Améliorez les tests existants
- Documentez les scénarios de test

#### 🎨 **Interface Utilisateur**
- Améliorez l'accessibilité
- Optimisez l'expérience mobile
- Créez de nouveaux composants
- Améliorez le design system

---

## 🛠️ **Configuration de l'Environnement**

### **Prérequis**
- **Python** 3.8+ avec pip
- **Node.js** 18+ avec npm
- **Git** pour le contrôle de version
- **PostgreSQL** 13+ ou SQLite pour le développement
- **Redis** 6+ (optionnel pour le développement)

### **Installation**

#### **1. Fork et Clone**
```bash
# Fork le projet sur GitHub puis :
git clone https://github.com/VOTRE_USERNAME/appget.git
cd appget

# Ajouter le remote upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/appget.git
```

#### **2. Configuration Backend**
```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dépendances de développement

# Configuration
cp .env.example .env
# Éditez .env selon vos besoins

# Migrations
python manage.py migrate
python manage.py createsuperuser
```

#### **3. Configuration Frontend**
```bash
cd frontend

# Installer les dépendances
npm install

# Configuration
cp .env.example .env.local
# Éditez .env.local selon vos besoins
```

#### **4. Validation de l'Installation**
```bash
# Depuis la racine du projet
python validate_features.py
```

### **Démarrage des Services**

#### **Développement Manuel**
```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Celery (optionnel)
cd backend
celery -A schedule_management worker --loglevel=info
```

#### **Développement Docker**
```bash
# Démarrage complet
docker-compose up -d

# Logs en temps réel
docker-compose logs -f web
```

---

## 📏 **Standards de Code**

### **Backend Python/Django**

#### **Style de Code**
- **PEP 8** pour le style Python
- **Black** pour le formatage automatique
- **isort** pour l'organisation des imports
- **flake8** pour la vérification statique

```bash
# Formatage automatique
black .
isort .

# Vérification
flake8 .
```

#### **Structure des Modules**
```
module_name/
├── __init__.py
├── admin.py          # Configuration admin Django
├── apps.py           # Configuration de l'app
├── models.py         # Modèles de données
├── views.py          # Vues API REST
├── serializers.py    # Sérialiseurs DRF
├── urls.py           # Configuration des URLs
├── permissions.py    # Permissions personnalisées
├── tasks.py          # Tâches Celery
├── utils.py          # Fonctions utilitaires
├── signals.py        # Signaux Django
├── tests/            # Tests du module
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_utils.py
└── migrations/       # Migrations de base de données
```

#### **Conventions de Nommage**
- **Classes** : `PascalCase` (ex: `GradeScale`)
- **Fonctions/Variables** : `snake_case` (ex: `calculate_average`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_FILE_SIZE`)
- **Fichiers** : `snake_case.py` (ex: `grade_calculator.py`)

#### **Documentation du Code**
```python
class GradeCalculator:
    """
    Calculateur de notes avec support pour différentes échelles.
    
    Cette classe fournit des méthodes pour calculer les moyennes,
    convertir les notes en lettres, et générer des relevés.
    
    Attributes:
        scale (GradeScale): L'échelle de notation utilisée
        precision (int): Nombre de décimales pour les calculs
    """
    
    def calculate_weighted_average(self, grades: List[Grade]) -> float:
        """
        Calcule la moyenne pondérée d'une liste de notes.
        
        Args:
            grades: Liste des notes à inclure dans le calcul
            
        Returns:
            La moyenne pondérée arrondie selon la précision
            
        Raises:
            ValueError: Si la liste est vide ou contient des notes invalides
            
        Example:
            >>> calculator = GradeCalculator(scale=french_scale)
            >>> average = calculator.calculate_weighted_average([grade1, grade2])
            >>> print(f"Moyenne: {average}")
        """
```

### **Frontend TypeScript/React**

#### **Style de Code**
- **ESLint** pour les règles de code
- **Prettier** pour le formatage
- **TypeScript strict** mode activé
- **Hooks** React préférés aux classes

```bash
# Vérification et formatage
npm run lint
npm run format

# Vérification des types
npm run type-check
```

#### **Structure des Composants**
```
components/
├── common/           # Composants réutilisables
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   └── Modal/
├── grades/           # Composants spécifiques aux notes
├── absences/         # Composants spécifiques aux absences
└── pdf/              # Composants spécifiques aux PDF
```

#### **Conventions de Nommage**
- **Composants** : `PascalCase` (ex: `StudentGradesView`)
- **Hooks** : `camelCase` avec préfixe `use` (ex: `useGrades`)
- **Types/Interfaces** : `PascalCase` (ex: `Grade`, `StudentData`)
- **Fichiers** : `PascalCase.tsx` pour composants, `camelCase.ts` pour utilitaires

#### **Documentation des Composants**
```typescript
/**
 * Composant d'affichage des notes d'un étudiant.
 * 
 * Ce composant affiche les notes, calcule les moyennes,
 * et permet l'export de relevés PDF.
 * 
 * @param studentId - ID de l'étudiant (optionnel si utilisateur courant)
 * @param isCurrentUser - Si true, affiche les données de l'utilisateur connecté
 */
interface StudentGradesViewProps {
  /** ID de l'étudiant dont afficher les notes */
  studentId?: number;
  /** Indique si c'est l'utilisateur courant */
  isCurrentUser?: boolean;
}

export const StudentGradesView: React.FC<StudentGradesViewProps> = ({
  studentId,
  isCurrentUser = false
}) => {
  // Implementation...
};
```

#### **Types TypeScript**
```typescript
// Toujours typer les props des composants
interface ComponentProps {
  required: string;
  optional?: number;
  callback: (data: SomeType) => void;
}

// Utiliser des unions pour les valeurs limitées
type NotificationPriority = 'low' | 'medium' | 'high' | 'critical';

// Préférer les interfaces aux types pour les objets
interface Grade {
  id: number;
  value: number;
  maxValue: number;
  coefficient: number;
  studentId: number;
  evaluationId: number;
}
```

---

## 🔄 **Process de Développement**

### **Workflow Git**

#### **1. Préparation**
```bash
# Synchroniser avec upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

#### **2. Créer une Branche**
```bash
# Convention de nommage des branches
git checkout -b feature/grade-calculator    # Nouvelle fonctionnalité
git checkout -b fix/absence-upload-bug      # Correction de bug
git checkout -b docs/api-documentation      # Documentation
git checkout -b refactor/grade-models       # Refactoring
```

#### **3. Développement**
```bash
# Commits fréquents avec messages clairs
git add .
git commit -m "feat(grades): add weighted average calculation

- Implement GradeCalculator class
- Add support for different grade scales
- Include comprehensive unit tests
- Update API documentation

Fixes #123"
```

#### **4. Tests et Validation**
```bash
# Backend
cd backend
python manage.py test
python -m pytest
flake8 .
black --check .

# Frontend
cd frontend
npm test
npm run lint
npm run type-check
npm run build
```

#### **5. Push et Pull Request**
```bash
git push origin feature/grade-calculator
# Ensuite créer la PR sur GitHub
```

### **Messages de Commit**

#### **Format**
```
type(scope): description courte

Description détaillée optionnelle expliquant le POURQUOI
plutôt que le COMMENT.

Fixes #123
Closes #456
```

#### **Types**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation uniquement
- `style`: Formatage, points-virgules manquants, etc.
- `refactor`: Refactoring sans changement fonctionnel
- `test`: Ajout ou correction de tests
- `chore`: Maintenance (build, CI, dépendances)

#### **Exemples**
```bash
feat(grades): add PDF export for transcripts
fix(absences): resolve file upload validation error
docs(api): update authentication endpoints documentation
refactor(notifications): extract email service to separate module
test(grades): add integration tests for grade calculations
chore(deps): update Django to 5.0.1
```

---

## 🧪 **Tests**

### **Backend Django**

#### **Structure des Tests**
```python
# tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from grades.models import Grade, Evaluation

User = get_user_model()

class GradeModelTest(TestCase):
    def setUp(self):
        """Configuration commune à tous les tests."""
        self.user = User.objects.create_user(
            username='test_student',
            email='student@test.com',
            role='student'
        )
        
    def test_grade_percentage_calculation(self):
        """Test du calcul de pourcentage d'une note."""
        grade = Grade.objects.create(
            student=self.user,
            grade_value=15.5,
            max_grade=20.0
        )
        
        self.assertEqual(grade.percentage, 77.5)
        
    def test_grade_validation(self):
        """Test de la validation des notes."""
        with self.assertRaises(ValidationError):
            Grade.objects.create(
                student=self.user,
                grade_value=25.0,  # Supérieur au maximum
                max_grade=20.0
            )
```

#### **Tests d'API**
```python
# tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class GradeAPITest(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            password='testpass123',
            role='student'
        )
        self.client.force_authenticate(user=self.student)
        
    def test_get_student_grades(self):
        """Test récupération des notes d'un étudiant."""
        url = reverse('grades:my-grades')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
    def test_create_grade_requires_teacher_permission(self):
        """Test que seuls les enseignants peuvent créer des notes."""
        url = reverse('grades:grade-list')
        data = {
            'student': self.student.id,
            'grade_value': 15.0,
            'max_grade': 20.0
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

#### **Commandes de Test**
```bash
# Tests complets
python manage.py test

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
coverage html

# Tests spécifiques
python manage.py test grades.tests.test_models
python manage.py test grades.tests.test_models.GradeModelTest.test_grade_percentage_calculation

# Tests avec pytest
pytest
pytest grades/tests/
pytest -v --tb=short
```

### **Frontend React**

#### **Tests de Composants**
```typescript
// components/grades/__tests__/StudentGradesView.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StudentGradesView } from '../StudentGradesView';
import { useGrades } from '../../../hooks/useEnhancedFeatures';

// Mock du hook
jest.mock('../../../hooks/useEnhancedFeatures');
const mockUseGrades = useGrades as jest.MockedFunction<typeof useGrades>;

describe('StudentGradesView', () => {
  beforeEach(() => {
    mockUseGrades.mockReturnValue({
      grades: [],
      summaries: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
      exportTranscript: jest.fn()
    });
  });

  it('should render student grades correctly', () => {
    render(<StudentGradesView studentId={1} />);
    
    expect(screen.getByText('Résultats par matière')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /export pdf/i })).toBeInTheDocument();
  });

  it('should handle PDF export', async () => {
    const mockExportTranscript = jest.fn().mockResolvedValue('job-123');
    mockUseGrades.mockReturnValue({
      ...mockUseGrades(),
      exportTranscript: mockExportTranscript
    });

    render(<StudentGradesView studentId={1} />);
    
    const exportButton = screen.getByRole('button', { name: /export pdf/i });
    await userEvent.click(exportButton);
    
    await waitFor(() => {
      expect(mockExportTranscript).toHaveBeenCalledWith({
        include_details: true,
        format: 'A4'
      });
    });
  });
});
```

#### **Tests d'Intégration**
```typescript
// __tests__/integration/gradeWorkflow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { GradeManagement } from '../components/grades/GradeManagement';

// Mock du serveur API
const server = setupServer(
  rest.get('/api/grades/my_grades/', (req, res, ctx) => {
    return res(ctx.json({
      results: [
        {
          id: 1,
          grade_value: 15.5,
          max_grade: 20,
          evaluation_name: 'Examen Final'
        }
      ]
    }));
  }),
  
  rest.post('/api/pdf-export/export/create/', (req, res, ctx) => {
    return res(ctx.json({
      job_id: 'pdf-job-123',
      status: 'pending'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Grade Workflow Integration', () => {
  it('should complete full grade viewing and export workflow', async () => {
    render(<GradeManagement studentId={1} />);
    
    // Attendre le chargement des données
    await waitFor(() => {
      expect(screen.getByText('Examen Final')).toBeInTheDocument();
    });
    
    // Cliquer sur export PDF
    const exportButton = screen.getByRole('button', { name: /export/i });
    await userEvent.click(exportButton);
    
    // Vérifier que l'export a été déclenché
    await waitFor(() => {
      expect(screen.getByText(/export lancé/i)).toBeInTheDocument();
    });
  });
});
```

#### **Commandes de Test Frontend**
```bash
# Tests complets
npm test

# Tests avec couverture
npm run test:coverage

# Tests en mode watch
npm run test:watch

# Tests spécifiques
npm test -- --testPathPattern=grades
npm test -- --testNamePattern="export"

# Tests end-to-end (si configurés)
npm run test:e2e
```

---

## 📚 **Documentation**

### **Types de Documentation**

#### **Code Documentation**
- **Docstrings** pour toutes les fonctions publiques
- **Commentaires** pour la logique complexe
- **Type hints** Python complets
- **TypeScript types** explicites

#### **API Documentation**
- **OpenAPI/Swagger** pour les endpoints REST
- **Exemples** de requêtes et réponses
- **Codes d'erreur** documentés
- **Authentification** expliquée

#### **User Documentation**
- **Guides d'utilisation** par rôle
- **Tutoriels** pas-à-pas
- **FAQ** pour les problèmes courants
- **Captures d'écran** annotées

### **Génération de Documentation**

#### **Backend**
```bash
# Documentation API avec Swagger
python manage.py spectacular --file schema.yml

# Documentation code avec Sphinx
cd docs/
make html
```

#### **Frontend**
```bash
# Documentation composants avec Storybook
npm run storybook

# Documentation TypeScript
npm run docs:generate
```

---

## 📤 **Pull Requests**

### **Checklist Avant Soumission**

#### **Code Quality**
- [ ] Code formaté selon les standards
- [ ] Pas de warnings linter
- [ ] Types TypeScript corrects
- [ ] Pas de code dupliqué

#### **Tests**
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Couverture de test acceptable (>80%)
- [ ] Tests manuels effectués

#### **Documentation**
- [ ] Docstrings/commentaires ajoutés
- [ ] README mis à jour si nécessaire
- [ ] Changelog mis à jour
- [ ] API doc mise à jour

#### **Sécurité**
- [ ] Pas de secrets/clés exposés
- [ ] Validation des entrées utilisateur
- [ ] Permissions vérifiées
- [ ] Pas de vulnérabilités introduites

### **Template de Pull Request**

```markdown
## 📋 Description
Décrivez brièvement les changements apportés et pourquoi ils sont nécessaires.

Fixes #(numéro de l'issue)

## 🔄 Type de Changement
- [ ] Bug fix (changement non-breaking qui corrige un problème)
- [ ] Nouvelle fonctionnalité (changement non-breaking qui ajoute une fonctionnalité)
- [ ] Breaking change (fix ou fonctionnalité qui casserait la fonctionnalité existante)
- [ ] Documentation uniquement

## 🧪 Comment Tester
Décrivez les étapes pour tester vos changements :
1. Aller à '...'
2. Cliquer sur '....'
3. Faire défiler jusqu'à '....'
4. Voir l'erreur/amélioration

## 📷 Captures d'Écran (si applicable)
Ajoutez des captures d'écran pour illustrer les changements visuels.

## ✅ Checklist
- [ ] Mon code suit les guidelines de style du projet
- [ ] J'ai effectué une auto-review de mon code
- [ ] J'ai commenté mon code, particulièrement dans les zones difficiles
- [ ] J'ai fait les changements correspondants à la documentation
- [ ] Mes changements ne génèrent pas de nouveaux warnings
- [ ] J'ai ajouté des tests qui prouvent que ma correction est efficace ou que ma fonctionnalité marche
- [ ] Les tests unitaires nouveaux et existants passent localement avec mes changements
- [ ] Toutes les dépendances nécessaires ont été ajoutées
```

### **Process de Review**

#### **Pour les Reviewers**
1. **Compréhension** - Le changement est-il clair ?
2. **Fonctionnalité** - Le code fait-il ce qu'il prétend faire ?
3. **Performance** - Y a-t-il des impacts performance ?
4. **Sécurité** - Y a-t-il des risques de sécurité ?
5. **Maintenabilité** - Le code est-il maintenable ?

#### **Commentaires de Review**
```markdown
# Suggestions constructives
💡 **Suggestion**: Pourriez-vous extraire cette logique dans une fonction séparée pour améliorer la lisibilité ?

# Questions de clarification
❓ **Question**: Pourquoi avez-vous choisi cette approche plutôt que X ?

# Approbation avec suggestions mineures
✅ **LGTM** avec quelques suggestions mineures ci-dessus.

# Demande de changements
🔄 **Changements requis**: Veuillez corriger les problèmes de sécurité mentionnés avant le merge.
```

---

## 🐛 **Signalement de Bugs**

### **Template d'Issue Bug**

```markdown
---
name: Bug Report
about: Créer un rapport pour nous aider à améliorer AppGET
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Description du Bug
Une description claire et concise de ce qui ne fonctionne pas.

## 🔄 Étapes pour Reproduire
1. Aller à '...'
2. Cliquer sur '....'
3. Faire défiler jusqu'à '....'
4. Voir l'erreur

## ✅ Comportement Attendu
Une description claire et concise de ce que vous attendiez qu'il arrive.

## 📷 Captures d'Écran
Si applicable, ajoutez des captures d'écran pour expliquer votre problème.

## 🖥️ Informations d'Environnement
 - OS: [ex. iOS, Windows, Linux]
 - Navigateur: [ex. chrome, safari]
 - Version d'AppGET: [ex. 2.0.0]
 - Python: [ex. 3.11]
 - Node.js: [ex. 18.15]

## 📝 Logs d'Erreur
```
Coller ici les logs d'erreur pertinents
```

## 📋 Contexte Additionnel
Ajoutez tout autre contexte à propos du problème ici.

## 🔧 Solutions Tentées
Décrivez ce que vous avez déjà essayé pour résoudre le problème.
```

### **Priorités des Bugs**

#### **🔴 Critique**
- Crash de l'application
- Perte de données
- Faille de sécurité
- Fonctionnalité principale cassée

#### **🟠 Élevée**
- Fonctionnalité importante affectée
- Performance significativement dégradée
- Bug affectant plusieurs utilisateurs

#### **🟡 Moyenne**
- Fonctionnalité secondaire affectée
- Workaround disponible
- Bug cosmétique visible

#### **🟢 Faible**
- Bug cosmétique mineur
- Amélioration suggérée
- Documentation incorrecte

---

## 💬 **Support**

### **Canaux de Communication**

#### **GitHub Discussions**
- **Général** : Questions et discussions générales
- **Aide** : Demande d'aide pour l'utilisation
- **Idées** : Propositions d'améliorations
- **Q&A** : Questions techniques

#### **GitHub Issues**
- **Bugs** : Signalement de problèmes
- **Features** : Demandes de nouvelles fonctionnalités
- **Security** : Rapports de sécurité (privés)

#### **Email**
- **Support** : support@appget.com
- **Sécurité** : security@appget.com
- **Contribution** : contrib@appget.com

### **Temps de Réponse**
- **Issues critiques** : 24-48h
- **Issues normales** : 1-2 semaines
- **Pull Requests** : 3-5 jours ouvrés
- **Questions support** : 1-3 jours ouvrés

### **Ressources Utiles**
- 📚 [Documentation complète](./NOUVELLES_FONCTIONNALITES.md)
- 🚀 [Guide de déploiement](./DEPLOIEMENT_PRODUCTION.md)
- 📋 [Changelog](./CHANGELOG.md)
- 🧪 [Tests automatisés](./backend/tests/)

---

## 🏆 **Reconnaissance des Contributeurs**

### **Types de Contributions Reconnues**
- 💻 **Code** - Développement de fonctionnalités et corrections
- 📚 **Documentation** - Amélioration de la documentation
- 🐛 **Tests** - Tests et assurance qualité
- 🎨 **Design** - Interface utilisateur et expérience
- 🔒 **Sécurité** - Audits et améliorations de sécurité
- 🌍 **Traduction** - Internationalisation
- 💡 **Idées** - Suggestions et planification
- 👀 **Review** - Révision de code et mentoring

### **Hall of Fame**
Les contributeurs significatifs seront reconnus dans le README principal avec leurs contributions spécifiques.

---

## 📄 **Licence**

En contribuant à AppGET, vous acceptez que vos contributions soient licenciées sous la même licence que le projet (MIT License).

---

## 🙏 **Remerciements**

Merci de prendre le temps de contribuer à AppGET ! Chaque contribution, petite ou grande, aide à améliorer cette plateforme pour la communauté éducative.

Votre participation fait la différence ! 🚀

---

*Ce guide de contribution est un document vivant. N'hésitez pas à proposer des améliorations !*
