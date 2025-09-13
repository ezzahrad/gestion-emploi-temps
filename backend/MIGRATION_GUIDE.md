# Guide de Résolution des Migrations - appGET

## Problème
Dépendance circulaire entre `authentication.User` et `core.Department`:
- `User.department` référence `Department`  
- `Department.head` référence `User`

## Solution Automatique (RECOMMANDÉE)

### Option 1: Script Python
```bash
cd backend
python resolve_migrations.py
```

### Option 2: Script Batch (Windows)
```bash
cd backend
resolve_migrations.bat
```

## Solution Manuelle

### Phase 1: Migrations de base

1. **Les champs problématiques sont déjà commentés** dans `core/models.py`:
   - `Department.head` 
   - `Program.head`

2. **Créer les migrations de base:**
```bash
python manage.py makemigrations authentication
python manage.py makemigrations core
python manage.py migrate
```

### Phase 2: Ajout des champs head

3. **Restaurer le modèle complet:**
```bash
copy core\models_complete.py core\models.py
```

4. **Créer et appliquer les migrations finales:**
```bash
python manage.py makemigrations core
python manage.py makemigrations schedule  
python manage.py makemigrations notifications
python manage.py migrate
```

## Vérification

Vérifier que toutes les migrations sont appliquées:
```bash
python manage.py showmigrations
```

Toutes les apps doivent avoir des [X] devant leurs migrations.

## En cas d'erreur

1. **Sauvegarder la base de données** si elle contient des données
2. **Supprimer la base de données** et recommencer
3. **Vérifier que PostgreSQL fonctionne** correctement
4. **Exécuter à nouveau** le script de résolution

## Structure finale attendue

```
backend/
├── authentication/migrations/
│   ├── 0001_initial.py
│   └── __init__.py
├── core/migrations/
│   ├── 0001_initial.py
│   ├── 0002_department_head_program_head.py
│   └── __init__.py  
├── schedule/migrations/
│   ├── 0001_initial.py
│   └── __init__.py
├── notifications/migrations/
│   ├── 0001_initial.py
│   └── __init__.py
```

## Scripts créés

- `resolve_migrations.py` - Script Python automatisé
- `resolve_migrations.bat` - Script batch Windows
- `core/models_complete.py` - Modèle complet avec champs head
- Ce guide: `MIGRATION_GUIDE.md`
