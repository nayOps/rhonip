# Guide de test des nouveaux dashboards

## ✅ Ce qui a été fait

1. ✅ Migration créée et appliquée : `core/migrations/0005_announcement.py`
2. ✅ Modèle `Announcement` importé dans le conteneur
3. ✅ Templates copiés dans le conteneur :
   - `template/home_employee.html`
   - `template/home_admin.html`
4. ✅ Vue `core/views/home.py` mise à jour dans le conteneur
5. ✅ 5 annonces de test créées dans la base de données
6. ✅ Serveur redémarré

## 🧪 Tests à effectuer

### Test 1 : Dashboard Employé (Employé normal)

**Prérequis** : Avoir un compte employé normal (ex: `david.kalonji@onip.cd`)

**Étapes** :
1. Se connecter avec un compte employé normal
2. Accéder à l'URL : `http://localhost:8000/`
3. Vérifier que le **Dashboard Personnel** s'affiche

**Éléments à vérifier** :

#### Sidebar gauche :
- ✅ Logo et nom de l'organisation
- ✅ Menu "Dashboard" (actif)
- ✅ Menu "Leave Requests" (si permission `leave.view_leave`)
- ✅ Menu "Projects" (si permission `mission.view_mission`)
- ✅ Menu "Training" (si permission `training.view_training`)
- ✅ Section "Internal Tools" avec "Resources" et "Settings"
- ✅ Profil utilisateur en bas avec photo et nom

#### Contenu principal :
- ✅ Section de bienvenue avec nom et photo de l'employé
- ✅ Carte "My Balance" :
  - Remaining Leave (jours et statut)
  - Training Hours (heures et statut)
- ✅ Section "My Workflow" :
  - Liste des tâches en attente (congés, missions, etc.)
  - Bouton "View All"
- ✅ Section "Recent Documents" (peut être vide pour l'instant)
- ✅ Sidebar droite :
  - Quick Links (Demander un congé, Soumettre un rapport, Réserver une salle)
  - Announcements (doit afficher les annonces actives)
  - Tip of the day

**Données attendues** :
- `remaining_leave.days` : Nombre de jours de congé restants
- `remaining_leave.status` : Statut (ex: "Accrued", "Exhausted")
- `training_hours.hours` : Heures de formation
- `training_hours.status` : Statut (ex: "In Progress")
- `workflow_tasks` : Liste des tâches en attente
- `announcements` : Liste des annonces actives (doit afficher au moins 2-3 annonces)

---

### Test 2 : Dashboard Admin (Admin/Staff)

**Prérequis** : Avoir un compte admin ou staff

**Étapes** :
1. Se connecter avec un compte admin/staff
2. Accéder à l'URL : `http://localhost:8000/`
3. Vérifier que le **Dashboard Admin** s'affiche

**Éléments à vérifier** :

#### Sidebar gauche :
- ✅ Logo et nom de l'organisation
- ✅ Menu "Dashboard" (actif)
- ✅ Menu "Personnel" (si permission `employee.view_employee`)
- ✅ Menu "Leaves" (si permission `leave.view_leave`)
- ✅ Menu "Missions" (si permission `mission.view_mission`)
- ✅ Menu "Training" (si permission `training.view_training`)
- ✅ Menu "Notifications" avec badge de compteur
- ✅ Bouton "Logout" en bas

#### Header :
- ✅ Barre de recherche globale
- ✅ Icône de notifications avec badge
- ✅ Profil utilisateur avec photo et nom

#### Contenu principal :
- ✅ Bannière de sécurité (Security Notice)
- ✅ 4 cartes KPI :
  - Total Employees (nombre total)
  - On Leave (nombre aujourd'hui)
  - Pending Evaluations (nombre)
  - Active Contracts (nombre)
- ✅ Section "Quick Actions" avec 8 boutons :
  - Add Employee, New Leave Request, Create Mission, Schedule Training, etc.
- ✅ Tableau "Leave Requests to Validate" :
  - Colonnes : Employee, Period, Type, Actions
  - Boutons Approve/Reject pour chaque demande
  - Bouton "View All"
- ✅ Sidebar droite :
  - Alerts & Activities
  - Monthly Birthdays
  - System Status

**Données attendues** :
- `total_employees` : Nombre total d'employés
- `on_leave_today` : Nombre d'employés en congé aujourd'hui
- `pending_evaluations` : Nombre d'évaluations en attente (peut être 0)
- `active_contracts` : Nombre de contrats actifs (peut être 0)
- `pending_leaves` : Liste des congés en attente de validation

---

## 🐛 Dépannage

### Si le dashboard employé ne s'affiche pas :
1. Vérifier que l'utilisateur n'est **pas** superuser ou staff
2. Vérifier que l'utilisateur a un `employee` associé
3. Vérifier les logs : `docker logs onip-rh-server-1 --tail 50`

### Si le dashboard admin ne s'affiche pas :
1. Vérifier que l'utilisateur est superuser ou staff
2. Vérifier les logs : `docker logs onip-rh-server-1 --tail 50`

### Si les données ne s'affichent pas :
1. Vérifier que les méthodes dans `core/views/home.py` retournent les bonnes données
2. Vérifier les erreurs dans la console du navigateur (F12)
3. Vérifier les logs Django : `docker logs onip-rh-server-1 --tail 100`

### Si les annonces ne s'affichent pas :
1. Vérifier qu'il y a des annonces actives :
   ```bash
   docker exec onip-rh-server-1 sh -c "cd /app/backend && python manage.py shell -c \"from core.models import Announcement; print(Announcement.objects.filter(is_active=True).count())\""
   ```
2. Vérifier que `announcements` est bien dans le contexte de la vue

---

## 📝 Notes

- Les templates utilisent Tailwind CSS via CDN
- Les icônes utilisent Material Symbols
- Le design est identique aux fichiers de référence (`admin/code.html` et `personnal/code.html`)
- Les données sont filtrées selon les permissions de l'utilisateur
- Les menus sont conditionnels selon les permissions

---

## ✅ Checklist de validation

### Dashboard Employé :
- [ ] Sidebar s'affiche correctement
- [ ] Section de bienvenue avec nom et photo
- [ ] Cartes "My Balance" affichent des données
- [ ] Section "My Workflow" affiche les tâches en attente
- [ ] Annonces s'affichent dans la sidebar droite
- [ ] Tous les liens fonctionnent

### Dashboard Admin :
- [ ] Sidebar s'affiche correctement
- [ ] Header avec recherche et notifications
- [ ] Bannière de sécurité s'affiche
- [ ] 4 cartes KPI affichent des données
- [ ] Section "Quick Actions" avec tous les boutons
- [ ] Tableau "Leave Requests to Validate" s'affiche
- [ ] Sidebar droite avec Alerts, Birthdays, System Status
- [ ] Tous les liens fonctionnent

---

**Prochaine étape** : Tester avec un compte employé normal, puis avec un compte admin.
