# GUIDE ÉTAPE PAR ÉTAPE - RÉSOLUTION MIGRATIONS

## SITUATION ACTUELLE ✅
- ✅ Anciennes migrations supprimées (renommées en .old)
- ✅ Modèles core sans champs 'head' (pas de circularité)  
- ✅ Prêt pour création propre des migrations

## COMMANDES À EXÉCUTER DANS L'ORDRE

### PHASE 1: Migrations de base

```powershell
# Dans PowerShell, répertoire: C:\Users\HP\Downloads\appGET\backend

# 1. Créer migration authentication
python manage.py makemigrations authentication

# 2. Créer migration core  
python manage.py makemigrations core

# 3. Appliquer ces migrations
python manage.py migrate
```

### PHASE 2: Modèle complet

```powershell
# 4. Restaurer le modèle complet
Copy-Item core\models_complete.py core\models.py -Force

# 5. Créer migration pour les champs head
python manage.py makemigrations core

# 6. Créer migrations schedule
python manage.py makemigrations schedule

# 7. Créer migrations notifications  
python manage.py makemigrations notifications

# 8. Appliquer toutes les migrations
python manage.py migrate
```

### VÉRIFICATION
```powershell
# Vérifier que tout est OK
python manage.py showmigrations
```

## COMMANDES ALTERNATIVES (une par une)

Si une commande échoue, essayez ces alternatives:

### Pour PowerShell:
```powershell
.\resolve_migrations.ps1
```

### Pour Python:
```powershell
python clean_and_fix_migrations.py
```

## EN CAS DE PROBLÈME

Si une étape échoue:

1. **Arrêtez-vous** à cette étape
2. **Copiez l'erreur** complète
3. **Montrez-moi** l'erreur pour diagnostic
4. **Ne continuez pas** les étapes suivantes

## RÉSULTATS ATTENDUS

Après succès, vous devriez voir:
```
[X] authentication.0001_initial  
[X] core.0001_initial
[X] core.0002_department_head_program_head
[X] schedule.0001_initial
[X] notifications.0001_initial
```

## PROCHAINES ÉTAPES APRÈS SUCCÈS

```powershell
# Créer un admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Tester: http://127.0.0.1:8000/admin/
```
