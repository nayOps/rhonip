# 💰 Modèle de Monétisation ONIP - Système FGP

## 📋 Vue d'ensemble

Le système ONIP (Office National d'Identification de la Population) génère des revenus via la monétisation des services d'identité numérique fournis aux tiers (banques, institutions, entreprises).

---

## 🎯 MODÈLES DE MONÉTISATION

### 1️⃣ **Modèle Transactionnel (Pay-per-Use)**

#### **Principe**
Chaque authentification/vérification d'identité effectuée via l'API ONIP génère une transaction facturable.

#### **Types de Transactions**

| Type de Transaction | Description | Exemple d'Usage | Tarif Proposé |
|---------------------|-------------|----------------|---------------|
| **IDENTITY_VERIFY** | Vérification simple d'identité (nom, date de naissance) | Banque vérifie l'identité d'un client | 0,50$ USD |
| **BIOMETRIC_VERIFY** | Vérification biométrique (empreinte, visage) | Authentification biométrique en agence | 1,00$ USD |
| **IRIS_VERIFY** | Vérification par iris | Point de vente hautement sécurisé | 1,50$ USD |
| **FULL_IDENTITY_CHECK** | Vérification complète avec historique | Vérification pré-crédit | 2,00$ USD |
| **IDENTITY_SEARCH** | Recherche 1:N (déduplication) | Vérification pré-enrôlement | 3,00$ USD |
| **CREDENTIAL_ISSUE** | Émission de carte d'identité | Nouvelle carte nationale | 5,00$ USD |

#### **Implémentation Technique**

```sql
-- Table de facturation des transactions
CREATE TABLE onip_transaction (
    transaction_id UUID PRIMARY KEY,
    requestor_id VARCHAR(100) NOT NULL, -- Banque, institution
    transaction_type VARCHAR(50) NOT NULL,
    person_id VARCHAR(20), -- NIN (optionnel si recherche)
    api_endpoint VARCHAR(255),
    request_timestamp TIMESTAMPTZ DEFAULT NOW(),
    response_status VARCHAR(20), -- SUCCESS, FAILED, ERROR
    response_time_ms INTEGER,
    amount DECIMAL(10,2) NOT NULL, -- Montant facturé
    currency VARCHAR(3) DEFAULT 'USD',
    billing_status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, INVOICED, PAID
    invoice_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des clients (banques, institutions)
CREATE TABLE onip_client (
    client_id UUID PRIMARY KEY,
    client_code VARCHAR(50) UNIQUE NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    client_type VARCHAR(50), -- BANK, INSURANCE, TELCO, GOVERNMENT, PRIVATE
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    billing_model VARCHAR(20) DEFAULT 'TRANSACTIONAL', -- TRANSACTIONAL, SUBSCRIPTION, HYBRID
    credit_limit DECIMAL(12,2),
    current_balance DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ACTIVE', -- ACTIVE, SUSPENDED, BLOCKED
    contract_start_date DATE,
    contract_end_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tarification par type de transaction
CREATE TABLE onip_pricing (
    pricing_id UUID PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL UNIQUE,
    base_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    client_type VARCHAR(50), -- NULL = tarif général
    volume_discount_threshold INTEGER, -- Nombre de transactions/mois
    volume_discount_percentage DECIMAL(5,2),
    valid_from DATE NOT NULL,
    valid_to DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Factures
CREATE TABLE onip_invoice (
    invoice_id UUID PRIMARY KEY,
    client_id UUID REFERENCES onip_client(client_id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    billing_period_start DATE,
    billing_period_end DATE,
    total_amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_with_tax DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'DRAFT', -- DRAFT, SENT, PAID, OVERDUE
    due_date DATE,
    paid_date DATE,
    payment_reference VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2️⃣ **Modèle d'Abonnement (Subscription)**

#### **Principe**
Les clients payent un abonnement mensuel/annuel pour un quota de transactions inclus.

#### **Plans d'Abonnement**

| Plan | Quota Mensuel | Prix/Mois | Prix par Transaction Supplémentaire |
|------|---------------|-----------|-------------------------------------|
| **STARTER** | 1,000 transactions | 500$ USD | 0,40$ USD |
| **BUSINESS** | 10,000 transactions | 3,500$ USD | 0,35$ USD |
| **ENTERPRISE** | 100,000 transactions | 25,000$ USD | 0,25$ USD |
| **UNLIMITED** | Illimité | 50,000$ USD | Inclus |

```sql
CREATE TABLE onip_subscription (
    subscription_id UUID PRIMARY KEY,
    client_id UUID REFERENCES onip_client(client_id),
    plan_type VARCHAR(50) NOT NULL,
    quota_monthly INTEGER NOT NULL,
    used_quota INTEGER DEFAULT 0,
    billing_cycle VARCHAR(20) DEFAULT 'MONTHLY', -- MONTHLY, QUARTERLY, YEARLY
    start_date DATE NOT NULL,
    end_date DATE,
    auto_renew BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 3️⃣ **Modèle Hybride (Transactionnel + Abonnement)**

#### **Principe**
Combinaison : abonnement de base + paiement des transactions dépassant le quota.

#### **Exemple Concret : Banque ABC - Mois de Janvier 2025**

**Configuration du client :**
- Plan : **BUSINESS**
- Abonnement mensuel : **3,500$ USD**
- Quota inclus : **10,000 transactions/mois**
- Tarif transaction supplémentaire : **0,35$ USD**

**Activité réelle du mois :**

| Type de Transaction | Volume | Prix Unitaire | Coût Total |
|---------------------|--------|---------------|------------|
| IDENTITY_VERIFY (Ouverture comptes) | 3,500 | 0,50$ | 1,750$ |
| BIOMETRIC_VERIFY (Retraits DAB) | 8,200 | 1,00$ | 8,200$ |
| IRIS_VERIFY (Paiements sécurisés) | 2,300 | 1,50$ | 3,450$ |
| FULL_IDENTITY_CHECK (Vérifications pré-crédit) | 800 | 2,00$ | 1,600$ |
| **TOTAL TRANSACTIONS** | **14,800** | - | **15,000$** |

**Calcul de facturation :**

```
Étape 1 : Quota inclus utilisé
- Transactions dans le quota : 10,000 transactions
- Coût : 0$ (inclus dans l'abonnement de 3,500$)

Étape 2 : Transactions supplémentaires
- Transactions hors quota : 14,800 - 10,000 = 4,800 transactions
- Coût transactionnel : 4,800 × 0,35$ = 1,680$ USD

Étape 3 : Total mensuel
- Abonnement : 3,500$ USD
- Transactions supplémentaires : 1,680$ USD
- **TOTAL FACTURÉ : 5,180$ USD**

Économie réalisée vs modèle transactionnel pur :
- Coût si transactionnel : 15,000$ USD
- Coût avec modèle hybride : 5,180$ USD
- Économie : 9,820$ USD (65% de réduction)
```

**Détail de la répartition des transactions :**

```
Quota inclus (10,000 transactions) :
├─ IDENTITY_VERIFY : 3,500 transactions (gratuit)
├─ BIOMETRIC_VERIFY : 5,500 transactions (gratuit)
└─ IRIS_VERIFY : 1,000 transactions (gratuit)

Hors quota (4,800 transactions) :
├─ BIOMETRIC_VERIFY : 2,700 transactions × 0,35$ = 945$ USD
├─ IRIS_VERIFY : 1,300 transactions × 0,35$ = 455$ USD
└─ FULL_IDENTITY_CHECK : 800 transactions × 0,35$ = 280$ USD
```

**Facture mensuelle générée :**

```
═══════════════════════════════════════════════════════════════
FACTURE ONIP - BANQUE ABC
Période : 01/01/2025 - 31/01/2025
Facture #: ONIP-2025-01-ABC-001
═══════════════════════════════════════════════════════════════

ABONNEMENT BUSINESS
├─ Plan : BUSINESS (10,000 transactions/mois)
└─ Montant : 3,500.00$ USD

TRANSACTIONS SUPPLÉMENTAIRES
├─ Volume : 4,800 transactions
├─ Tarif unitaire : 0,35$ USD
└─ Montant : 1,680.00$ USD

═══════════════════════════════════════════════════════════════
TOTAL HT : 5,180.00$ USD
TVA (18%) : 932.40$ USD
TOTAL TTC : 6,112.40$ USD
═══════════════════════════════════════════════════════════════

Échéance : 15/02/2025
Méthode de paiement : Virement bancaire
```

#### **Avantages du Modèle Hybride**

1. **Prévisibilité** : Coût fixe mensuel pour les clients
2. **Flexibilité** : Pas de surcoût si usage faible
3. **Économies** : Réduction significative vs modèle transactionnel pur
4. **Scalabilité** : Adaptation automatique au volume réel

---

## 💳 EXEMPLES CONCRETS DE MONÉTISATION

### **Scénario 1 : Banque - Ouverture de Compte**

```
1. Client se présente en agence avec sa carte d'identité
2. Banque scanne la carte → appel API ONIP: IDENTITY_VERIFY
3. ONIP vérifie : NIN, nom, date de naissance → réponse: VALID/INVALID
4. Transaction enregistrée : 0,50$ USD
5. Si authentification biométrique : +1,00$ USD (BIOMETRIC_VERIFY)
6. Total : 1,50$ USD par ouverture de compte
```

### **Scénario 2 : Banque - Retrait DAB avec Biométrie**

```
1. Client utilise DAB avec authentification biométrique
2. Banque vérifie l'identité via API: BIOMETRIC_VERIFY
3. Transaction facturée : 1,00$ USD
4. Volume quotidien : 1,000 retraits × 1,00$ = 1,000$ USD/jour
5. Revenu mensuel estimé : 30,000$ USD
```

### **Scénario 3 : Institution Financière - Vérification Pré-Crédit**

```
1. Client demande un prêt
2. Institution vérifie l'identité complète : FULL_IDENTITY_CHECK
3. Transaction facturée : 2,00$ USD
4. Volume mensuel : 500 vérifications × 2,00$ = 1,000$ USD/mois
```

### **Scénario 4 : Point de Vente - Paiement Sécurisé**

```
1. Client paye avec authentification iris
2. Marchand vérifie via API: IRIS_VERIFY
3. Transaction facturée : 1,50$ USD
4. Volume : 10,000 paiements/mois × 1,50$ = 15,000$ USD/mois
```

---

## 📊 TABLEAU DE BORD DE MONÉTISATION

### **Métriques Clés**

```sql
-- Vue pour le tableau de bord financier
CREATE VIEW v_monetization_dashboard AS
SELECT 
    DATE_TRUNC('day', request_timestamp) as transaction_date,
    transaction_type,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(response_time_ms) as avg_response_time,
    COUNT(DISTINCT requestor_id) as active_clients
FROM onip_transaction
WHERE billing_status = 'PAID'
GROUP BY DATE_TRUNC('day', request_timestamp), transaction_type;

-- Revenus par client
CREATE VIEW v_client_revenue AS
SELECT 
    c.client_name,
    c.client_type,
    COUNT(t.transaction_id) as total_transactions,
    SUM(t.amount) as total_revenue,
    DATE_TRUNC('month', t.request_timestamp) as billing_month
FROM onip_client c
LEFT JOIN onip_transaction t ON c.client_id::VARCHAR = t.requestor_id
GROUP BY c.client_name, c.client_type, DATE_TRUNC('month', t.request_timestamp);
```

---

## 🔐 SÉCURITÉ ET CONTRÔLE D'ACCÈS

### **API Key Management**

```sql
CREATE TABLE onip_api_key (
    key_id UUID PRIMARY KEY,
    client_id UUID REFERENCES onip_client(client_id),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret_hash VARCHAR(255) NOT NULL,
    permissions JSONB, -- Liste des endpoints autorisés
    rate_limit INTEGER DEFAULT 1000, -- Requêtes/heure
    ip_whitelist TEXT[], -- IPs autorisées
    status VARCHAR(20) DEFAULT 'ACTIVE',
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### **Rate Limiting par Client**

- **STARTER** : 100 requêtes/heure
- **BUSINESS** : 1,000 requêtes/heure
- **ENTERPRISE** : 10,000 requêtes/heure
- **UNLIMITED** : Pas de limite

---

## 💰 REVENUS PROJETÉS (Exemple RDC)

### **Hypothèses de marché**

| Client Type | Nombre | Transactions/Mois | Prix/Transaction | Revenu Mensuel |
|-------------|--------|-------------------|------------------|----------------|
| **Banques** | 20 | 50,000 | 0,75$ (avg) | 750,000$ |
| **Télécoms** | 5 | 100,000 | 0,50$ | 50,000$ |
| **Assurances** | 10 | 10,000 | 1,00$ | 10,000$ |
| **Gouvernement** | 15 | 200,000 | 0,25$ | 50,000$ |
| **Autres** | 50 | 5,000 | 0,50$ | 12,500$ |
| **TOTAL** | **100** | **365,000** | - | **872,500$ USD/mois** |

### **Revenus Annuels Projetés : ~10,470,000$ USD/an**

---

## 🔄 PROCESSUS DE FACTURATION

### **Workflow Automatisé**

```
1. Transactions enregistrées en temps réel
   ↓
2. Agrégation quotidienne par client
   ↓
3. Génération mensuelle de factures (1er du mois)
   ↓
4. Envoi automatique par email aux clients
   ↓
5. Suivi des paiements (30 jours)
   ↓
6. Suspension automatique si impayé (>60 jours)
```

---

## 📋 INTÉGRATION API AVEC FACTURATION

### **Middleware de Facturation**

```python
# Exemple de middleware Django pour facturation automatique
class BillingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier API key et client
        api_key = request.headers.get('X-API-Key')
        client = OnipClient.objects.get(api_key=api_key)
        
        # Calculer le prix selon le type de transaction
        transaction_type = self._get_transaction_type(request.path)
        pricing = OnipPricing.objects.get(
            transaction_type=transaction_type,
            client_type=client.client_type
        )
        
        # Vérifier quota (si abonnement)
        if client.billing_model == 'SUBSCRIPTION':
            subscription = client.subscription
            if subscription.used_quota >= subscription.quota_monthly:
                # Dépassement → facturation transactionnelle
                amount = pricing.base_price
            else:
                # Dans le quota → gratuit
                amount = 0
        else:
            # Transactionnel → toujours facturé
            amount = pricing.base_price
        
        # Enregistrer la transaction
        OnipTransaction.objects.create(
            requestor_id=str(client.client_id),
            transaction_type=transaction_type,
            amount=amount,
            api_endpoint=request.path,
            response_status='PENDING'
        )
        
        response = self.get_response(request)
        
        # Mettre à jour le statut après réponse
        OnipTransaction.objects.filter(...).update(
            response_status='SUCCESS' if response.status_code == 200 else 'FAILED',
            response_time_ms=...
        )
        
        return response
```

---

## ✅ AVANTAGES DU MODÈLE

1. **Scalable** : Revenus proportionnels à l'usage
2. **Transparent** : Facturation claire et traçable
3. **Flexible** : Plans adaptés à chaque client
4. **Automatisé** : Peu d'intervention manuelle
5. **Rentable** : Revenus récurrents pour ONIP

---

**Date de création**: $(date)  
**Statut**: Modèle économique proposé  
**Conforme à**: OSIA - Open Standard Identity APIs

