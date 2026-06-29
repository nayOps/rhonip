# 🚀 COMMANDES DE DÉPLOIEMENT - SERVICE IRIS

## 📋 **ORDRE D'EXÉCUTION**

### **1. Build du Service Biométrique**

```bash
cd /home/nayops/Documents/strate/fgp

# Build l'image Docker
docker compose build biometric_service
```

**Durée estimée**: 5-10 minutes (première fois)

---

### **2. Démarrage des Services**

```bash
# Démarrer tous les services
docker compose up -d

# OU démarrer uniquement les services nécessaires
docker compose up -d postgres redis biometric_service
```

**Vérifier que les services sont démarrés**:
```bash
docker compose ps
```

---

### **3. Créer les Migrations Django**

```bash
# Créer les migrations pour l'app iris
docker compose exec biometric_service python manage.py makemigrations iris

# Afficher les migrations créées
docker compose exec biometric_service python manage.py showmigrations iris
```

**Output attendu**:
```
Migrations for 'iris':
  apps/iris/migrations/0001_initial.py
    - Create model IrisCaptureSession
    - Create model IrisCapture
    - Create model IrisTemplate
    - Create model IrisMatch
    - Create model IrisQualityLog
```

---

### **4. Appliquer les Migrations**

```bash
# Appliquer toutes les migrations
docker compose exec biometric_service python manage.py migrate

# OU appliquer uniquement les migrations iris
docker compose exec biometric_service python manage.py migrate iris
```

**Output attendu**:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, iris, sessions
Running migrations:
  Applying iris.0001_initial... OK
```

---

### **5. Créer un Superuser (Admin)**

```bash
docker compose exec biometric_service python manage.py createsuperuser
```

**Entrées demandées**:
- Username: `admin`
- Email: `admin@fgp.cd`
- Password: `admin2025` (ou votre choix)

---

### **6. Vérifier les Tables dans pgAdmin**

**Accéder à pgAdmin**:
- URL: http://localhost:5050/
- Email: `admin@fgp.cd`
- Password: `admin2025`

**Connexion au serveur**:
1. Add New Server
2. General → Name: `FGP Database`
3. Connection:
   - Host: `postgres`
   - Port: `5432`
   - Database: `fgp_db`
   - Username: `fgp_user`
   - Password: `fgp_password_2025`

**Tables créées**:
- `iris_capture_sessions`
- `iris_captures`
- `iris_templates`
- `iris_matches`
- `iris_quality_logs`

---

### **7. Vérifier l'API**

**Test de santé**:
```bash
curl http://localhost:8003/api/v1/biometrics/iris/sessions/
```

**Output attendu**:
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

**Accéder à l'admin Django**:
- URL: http://localhost:8003/admin/
- Username: `admin`
- Password: (celui créé à l'étape 5)

---

### **8. Test Complet - Créer une Session**

```bash
# Démarrer une session de capture
curl -X POST http://localhost:8003/api/v1/biometrics/iris/sessions/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_session_id": "test-enrollment-001",
    "operator_id": "operator-1",
    "station_id": "station-A"
  }'
```

**Output attendu**:
```json
{
  "success": true,
  "message": "Session de capture démarrée",
  "data": {
    "id": "...",
    "enrollment_session_id": "test-enrollment-001",
    "status": "IN_PROGRESS",
    "started_at": "...",
    "captures": [],
    "captures_count": 0,
    "valid_captures_count": 0
  }
}
```

---

## 🐛 **RÉSOLUTION DE PROBLÈMES**

### **Erreur: "relation ... does not exist"**

**Cause**: Migrations non appliquées  
**Solution**:
```bash
docker compose exec biometric_service python manage.py migrate
```

---

### **Erreur: "Could not connect to camera"**

**Cause**: Caméra USB non détectée ou pas de permissions  
**Solution**:
```bash
# Vérifier les devices vidéo
ls -la /dev/video*

# Redémarrer le service avec privilèges
docker compose restart biometric_service
```

---

### **Erreur: "Port 8003 already in use"**

**Cause**: Port déjà utilisé  
**Solution**:
```bash
# Trouver le processus
sudo lsof -i :8003

# Arrêter le processus ou changer le port dans docker-compose.yml
```

---

### **Logs en cas d'erreur**

```bash
# Voir les logs en temps réel
docker compose logs -f biometric_service

# Voir les 100 dernières lignes
docker compose logs --tail=100 biometric_service

# Entrer dans le container
docker compose exec biometric_service bash

# Vérifier les logs Django
cat /app/logs/biometric_service.log
```

---

## ✅ **CHECKLIST DE VALIDATION**

- [ ] Service `biometric_service` démarré (`docker compose ps`)
- [ ] Migrations créées (`showmigrations`)
- [ ] Migrations appliquées (`migrate`)
- [ ] Tables visibles dans pgAdmin (5 tables)
- [ ] Admin Django accessible (http://localhost:8003/admin/)
- [ ] API répond (http://localhost:8003/api/v1/biometrics/iris/sessions/)
- [ ] Session de test créée (cURL fonctionne)
- [ ] Logs sans erreur (`docker compose logs biometric_service`)

---

## 🎯 **TESTS FRONTEND**

### **1. Démarrer le Frontend**

```bash
# Si pas déjà démarré
docker compose up -d frontend

# Vérifier
curl http://localhost:3000
```

### **2. Accéder au Workflow d'Enrôlement**

1. Navigateur: http://localhost:3000
2. Aller à "Enrôlement"
3. Remplir le formulaire de base
4. Sélectionner une strate
5. Remplir les extensions
6. **Étape 4: Photo** → Capture ou upload
7. **Étape 5: Iris** → Le composant devrait charger

### **3. Mode de Test**

Le composant IrisCapture a **deux modes**:

**Mode Simulation** (par défaut):
- Variable `useSimulation = true`
- Pas d'appel API réel
- Simulation de 4 secondes
- Qualité aléatoire 75-100%

**Mode Réel**:
- Variable `useSimulation = false`
- Appels API au service biométrique
- Caméra USB requise
- Traitement réel

**Pour basculer en mode réel**, modifier:
```typescript
// frontend/src/components/biometrics/IrisCapture.tsx
const [useSimulation, setUseSimulation] = useState(false); // <- changer à false
```

---

## 📊 **VÉRIFICATION DES DONNÉES**

### **Depuis pgAdmin**

```sql
-- Compter les sessions
SELECT COUNT(*) FROM iris_capture_sessions;

-- Lister les captures
SELECT 
  id,
  eye_position,
  status,
  quality_score,
  is_valid,
  captured_at
FROM iris_captures
ORDER BY captured_at DESC
LIMIT 10;

-- Statistiques de qualité
SELECT 
  eye_position,
  AVG(quality_score) as avg_quality,
  COUNT(*) as total_captures,
  SUM(CASE WHEN is_valid THEN 1 ELSE 0 END) as valid_captures
FROM iris_captures
GROUP BY eye_position;
```

### **Depuis l'Admin Django**

1. http://localhost:8003/admin/
2. Iris biometric → Iris capture sessions
3. Cliquer sur une session pour voir les détails
4. Voir les captures liées

---

## 🔄 **REDÉMARRAGE COMPLET**

```bash
# Arrêter tous les services
docker compose down

# Nettoyer les volumes (ATTENTION: perte de données)
docker compose down -v

# Reconstruire
docker compose build

# Redémarrer
docker compose up -d

# Re-migrer
docker compose exec biometric_service python manage.py migrate
```

---

## 📞 **AIDE**

Si les étapes ne fonctionnent pas:

1. **Vérifier les logs**:
   ```bash
   docker compose logs biometric_service
   docker compose logs postgres
   docker compose logs redis
   ```

2. **Vérifier la connectivité**:
   ```bash
   docker compose exec biometric_service ping postgres
   docker compose exec biometric_service ping redis
   ```

3. **Tester la base de données**:
   ```bash
   docker compose exec biometric_service python manage.py dbshell
   ```

4. **Shell interactif Django**:
   ```bash
   docker compose exec biometric_service python manage.py shell
   ```

---

**PRÊT POUR LE TEST ! 🚀👁️**



