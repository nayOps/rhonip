# Instructions pour finaliser l'implémentation des dashboards

## ✅ Ce qui a été fait

1. **Modèle Announcement** : Créé et importé dans `core/models/__init__.py`
2. **Templates** : 
   - `template/home_employee.html` - Dashboard employé (design identique à `personnal/code.html`)
   - `template/home_admin.html` - Dashboard admin (design identique à `admin/code.html`)
3. **Vue Home** : Modifiée pour router automatiquement selon le rôle (employé/admin)
4. **Scripts utilitaires** :
   - `create_migration_announcement.py` - Pour créer et appliquer les migrations
   - `create_sample_announcements.py` - Pour créer des annonces de test

## 📋 Étapes pour finaliser

### 1. Créer et appliquer les migrations

Exécutez dans le conteneur Docker :

```bash
docker exec -it payday-backend-1 python create_migration_announcement.py
```

Ou manuellement :

```bash
docker exec -it payday-backend-1 python manage.py makemigrations core
docker exec -it payday-backend-1 python manage.py migrate
```

### 2. Créer des annonces de test (optionnel)

```bash
docker exec -it payday-backend-1 python create_sample_announcements.py
```

### 3. Redémarrer le serveur (si nécessaire)

```bash
docker restart payday-backend-1
```

### 4. Tester les dashboards

#### Test avec un employé normal :
1. Connectez-vous avec un compte employé normal (ex: `david.kalonji@onip.cd`)
2. Vous devriez voir le **Dashboard Personnel** (`home_employee.html`)
3. Vérifiez :
   - ✅ Sidebar avec navigation personnalisée
   - ✅ Section de bienvenue avec nom et photo
   - ✅ Cartes "My Balance" (Remaining Leave, Training Hours)
   - ✅ Section "My Workflow" (tâches en attente)
   - ✅ Section "Recent Documents"
   - ✅ Sidebar droite (Quick Links, Announcements, Tip of Day)

#### Test avec un admin/staff :
1. Connectez-vous avec un compte admin/staff
2. Vous devriez voir le **Dashboard Admin** (`home_admin.html`)
3. Vérifiez :
   - ✅ Sidebar avec navigation admin
   - ✅ Header avec recherche globale
   - ✅ Bannière de sécurité
   - ✅ 4 cartes KPI (Total Employees, On Leave, Pending Evaluations, Active Contracts)
   - ✅ Section "Quick Actions" (8 boutons)
   - ✅ Tableau "Leave Requests to Validate"
   - ✅ Sidebar droite (Alerts, Birthdays, System Status)

## 🔍 Vérifications supplémentaires

### Vérifier que les données sont correctement affichées :

1. **Dashboard Employé** :
   - `remaining_leave.days` et `remaining_leave.status` doivent s'afficher
   - `training_hours.hours` et `training_hours.status` doivent s'afficher
   - `workflow_tasks` doit lister les tâches en attente
   - `announcements` doit afficher les annonces actives

2. **Dashboard Admin** :
   - `total_employees` doit afficher le nombre total d'employés
   - `on_leave_today` doit afficher le nombre d'employés en congé aujourd'hui
   - `pending_leaves` doit lister les congés en attente de validation

## 🐛 Dépannage

### Si les migrations échouent :
- Vérifiez que le modèle `Announcement` est bien importé dans `core/models/__init__.py`
- Vérifiez que le conteneur Docker est bien démarré
- Vérifiez les logs : `docker logs payday-backend-1`

### Si les dashboards ne s'affichent pas correctement :
- Vérifiez que les templates sont bien dans `template/home_employee.html` et `template/home_admin.html`
- Vérifiez que la vue `core/views/home.py` route correctement selon le rôle
- Vérifiez les logs du serveur Django

### Si les données ne s'affichent pas :
- Vérifiez que les méthodes `_employee_dashboard()` et `_admin_dashboard()` retournent les bonnes données
- Vérifiez que les noms de variables dans les templates correspondent aux clés du contexte
- Vérifiez que les permissions sont correctement configurées

## 📝 Notes importantes

1. **Design identique** : Les templates ont été créés pour correspondre exactement aux fichiers de référence (`admin/code.html` et `personnal/code.html`)

2. **Données dynamiques** : Les templates utilisent des tags Django pour afficher les données dynamiques

3. **Permissions** : Les menus et sections sont filtrés selon les permissions de l'utilisateur

4. **Internationalisation** : Les templates utilisent `{% trans %}` pour la traduction

5. **Organisation** : Le logo et le nom de l'organisation sont récupérés depuis le modèle `Organization`

## 🎯 Prochaines étapes (optionnel)

1. Implémenter les fonctionnalités manquantes :
   - `recent_documents` pour le dashboard employé
   - `pending_evaluations` et `active_contracts` pour le dashboard admin
   - `alerts` et `activities` pour le dashboard admin
   - `birthdays` pour le dashboard admin

2. Améliorer les calculs :
   - Calculer correctement `remaining_leave` selon la politique de congés
   - Calculer `training_hours` depuis le modèle `Training`
   - Améliorer la détection des congés en attente

3. Ajouter des fonctionnalités :
   - Filtres et recherche dans les tableaux
   - Actions rapides depuis les dashboards
   - Notifications en temps réel
