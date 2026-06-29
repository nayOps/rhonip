# 📊 ARCHITECTURE DE LA BASE DE DONNÉES FGP

## 🗺️ DIAGRAMME PRINCIPAL - ARCHITECTURE GLOBALE

```mermaid
graph TB
    %% ============================================
    %% NŒUD CENTRAL
    %% ============================================
    PersonCore[💾 fgp_person_core<br/>TABLE CENTRALE<br/>27 variables obligatoires]
    
    %% ============================================
    %% TABLES SYSTÈME
    %% ============================================
    subgraph "📊 Données Système"
        Biometric[🔬 fgp_biometric<br/>Biométrie<br/>Photo, Empreintes, Iris]
        Strata[📋 fgp_strata_membership<br/>Appartenance aux Strates<br/>10 strates actives]
        Documents[📄 fgp_documents<br/>Documents & Pièces jointes]
        Audit[📝 fgp_audit_trail<br/>Traçabilité complète]
        ABIS[🔍 abis_matches<br/>Déduplication biométrique]
    end
    
    %% ============================================
    %% EXTENSIONS - STRATES
    %% ============================================
    subgraph "👶 Strate 1: ENFANT"
        ExtEnfant[👶 ext_enfants<br/>Informations tuteur<br/>Autorisation parentale]
    end
    
    subgraph "🎓 Strate 2: ÉLÈVE"
        ExtEleve[🎓 ext_eleves<br/>Établissement scolaire<br/>Niveau, Cycle, Année]
    end
    
    subgraph "🗳️ Strate 3: ÉLECTEUR"
        ExtElecteur[🗳️ ext_electeurs<br/>Centre de vote CENI<br/>Bureau, Circonscription]
    end
    
    subgraph "👮 Strate 4: PNC"
        ExtPNC[👮 ext_pnc<br/>Police Nationale<br/>Matricule, Grade, Unité]
    end
    
    subgraph "🎖️ Strate 5: FARDC"
        ExtFARDC[🎖️ ext_fardc<br/>Forces Armées<br/>Matricule, Grade, Zone]
    end
    
    subgraph "🔒 Strate 6: PRISONNIER"
        ExtPrison[🔒 ext_prison<br/>Détention<br/>Dossier judiciaire]
    end
    
    subgraph "🏕️ Strate 7: RÉFUGIÉ"
        ExtRefugie[🏕️ ext_refugies<br/>Réfugiés & Apatrides<br/>Numéro HCR, Pays origine]
    end
    
    subgraph "🌍 Strate 8: ÉTRANGER"
        ExtEtranger[🌍 ext_etrangers<br/>Étrangers en RDC<br/>Passeport, Visa, Permis]
    end
    
    subgraph "🚶 Strate 9: DÉPLACÉ"
        ExtDeplace[🚶 ext_deplaces<br/>Déplacés internes<br/>Lieu origine, Camp, Assistance]
    end
    
    subgraph "✈️ Strate 10: DIASPORA"
        ExtDiaspora[✈️ ext_diaspora<br/>Diaspora congolaise<br/>Pays résidence, Consulat]
    end
    
    %% ============================================
    %% GATEWAY D'ENRÔLEMENT
    %% ============================================
    subgraph "🔄 Enrollment Gateway"
        Sessions[📋 enrollment_sessions<br/>Sessions d'enrôlement]
        Validations[✅ enrollment_validations<br/>Validations règles métier]
        Events[📊 enrollment_events<br/>Événements & Logs]
        Receipts[🎫 enrollment_receipts<br/>Récépissés générés]
        Stats[📈 enrollment_statistics<br/>Statistiques monitoring]
    end
    
    %% ============================================
    %% RELATIONS PRINCIPALES
    %% ============================================
    PersonCore --> Biometric
    PersonCore --> Strata
    PersonCore --> Documents
    PersonCore --> Audit
    PersonCore --> ABIS
    
    PersonCore --> ExtEnfant
    PersonCore --> ExtEleve
    PersonCore --> ExtElecteur
    PersonCore --> ExtPNC
    PersonCore --> ExtFARDC
    PersonCore --> ExtPrison
    PersonCore --> ExtRefugie
    PersonCore --> ExtEtranger
    PersonCore --> ExtDeplace
    PersonCore --> ExtDiaspora
    
    Sessions --> Validations
    Sessions --> Events
    Sessions --> Receipts
    
    %% ============================================
    %% STYLES
    %% ============================================
    classDef central fill:#1976D2,stroke:#0D47A1,stroke-width:4px,color:#fff,font-weight:bold
    classDef system fill:#43A047,stroke:#2E7D32,stroke-width:2px,color:#fff
    classDef extension fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff
    classDef enrollment fill:#8E24AA,stroke:#6A1B9A,stroke-width:2px,color:#fff
    
    class PersonCore central
    class Biometric,Strata,Documents,Audit,ABIS system
    class ExtEnfant,ExtEleve,ExtElecteur,ExtPNC,ExtFARDC,ExtPrison,ExtRefugie,ExtEtranger,ExtDeplace,ExtDiaspora extension
    class Sessions,Validations,Events,Receipts,Stats enrollment
```

---

## 🔄 FLUX D'ENRÔLEMENT COMPLET

```mermaid
graph TB
    Start([🚀 Début Enrôlement])
    
    CreateSession[📝 Créer Session<br/>enrollment_sessions]
    CollectBase[👤 Collecter Données de Base<br/>27 variables obligatoires]
    
    SelectStrata{🎯 Sélectionner Strate<br/>10 choix disponibles}
    
    ExtEnfant[👶 Extension ENFANT<br/>ext_enfants]
    ExtEleve[🎓 Extension ÉLÈVE<br/>ext_eleves]
    ExtElecteur[🗳️ Extension ÉLECTEUR<br/>ext_electeurs]
    ExtPNC[👮 Extension PNC<br/>ext_pnc]
    ExtFARDC[🎖️ Extension FARDC<br/>ext_fardc]
    ExtPrison[🔒 Extension PRISONNIER<br/>ext_prison]
    ExtRefugie[🏕️ Extension RÉFUGIÉ<br/>ext_refugies]
    ExtEtranger[🌍 Extension ÉTRANGER<br/>ext_etrangers]
    ExtDeplace[🚶 Extension DÉPLACÉ<br/>ext_deplaces]
    ExtDiaspora[✈️ Extension DIASPORA<br/>ext_diaspora]
    
    CollectBio[🔬 Collecter Biométrie<br/>Photo, Empreintes, Iris]
    CollectDocs[📄 Scanner Documents<br/>Pièces d'identité]
    
    Validate[✅ Validation Complète<br/>enrollment_validations<br/>Schéma + Métier]
    
    ABISCheck{🔍 Vérification ABIS<br/>Déduplication biométrique<br/>abis_matches}
    
    Review[👁️ Révision Manuelle<br/>Match trouvé]
    Reject[❌ Rejeter Enrôlement<br/>Doublon détecté]
    
    GenerateNIN[🎲 Générer NIN<br/>CD-YYYY-NNNN-NNNNNNNNN]
    CreateMembership[📋 Créer Membership<br/>fgp_strata_membership]
    
    GenerateReceipt[🎫 Générer Récépissé<br/>enrollment_receipts<br/>QR Code]
    
    LogAudit[📝 Enregistrer Audit<br/>fgp_audit_trail]
    LogEvent[📊 Logger Événements<br/>enrollment_events]
    UpdateStats[📈 Mettre à jour Stats<br/>enrollment_statistics]
    
    End([✅ Enrôlement Terminé])
    
    Start --> CreateSession
    CreateSession --> CollectBase
    CollectBase --> SelectStrata
    
    SelectStrata -->|1| ExtEnfant
    SelectStrata -->|2| ExtEleve
    SelectStrata -->|3| ExtElecteur
    SelectStrata -->|4| ExtPNC
    SelectStrata -->|5| ExtFARDC
    SelectStrata -->|6| ExtPrison
    SelectStrata -->|7| ExtRefugie
    SelectStrata -->|8| ExtEtranger
    SelectStrata -->|9| ExtDeplace
    SelectStrata -->|10| ExtDiaspora
    
    ExtEnfant --> CollectBio
    ExtEleve --> CollectBio
    ExtElecteur --> CollectBio
    ExtPNC --> CollectBio
    ExtFARDC --> CollectBio
    ExtPrison --> CollectBio
    ExtRefugie --> CollectBio
    ExtEtranger --> CollectBio
    ExtDeplace --> CollectBio
    ExtDiaspora --> CollectBio
    
    CollectBio --> CollectDocs
    CollectDocs --> Validate
    Validate --> ABISCheck
    
    ABISCheck -->|✅ Pas de match| GenerateNIN
    ABISCheck -->|⚠️ Match trouvé| Review
    
    Review -->|Approuvé| GenerateNIN
    Review -->|Rejeté| Reject
    
    GenerateNIN --> CreateMembership
    CreateMembership --> GenerateReceipt
    GenerateReceipt --> LogAudit
    LogAudit --> LogEvent
    LogEvent --> UpdateStats
    UpdateStats --> End
    
    Reject --> LogEvent
    
    classDef startend fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff,font-weight:bold
    classDef process fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    classDef decision fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    classDef extension fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    classDef error fill:#F44336,stroke:#C62828,stroke-width:2px,color:#fff
    classDef success fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    
    class Start,End startend
    class CreateSession,CollectBase,CollectBio,CollectDocs,GenerateNIN,CreateMembership,GenerateReceipt,LogAudit,LogEvent,UpdateStats process
    class SelectStrata,ABISCheck decision
    class ExtEnfant,ExtEleve,ExtElecteur,ExtPNC,ExtFARDC,ExtPrison,ExtRefugie,ExtEtranger,ExtDeplace,ExtDiaspora extension
    class Reject error
    class Validate,Review success
```

---

## 🔗 RELATIONS ET CARDINALITÉS

```mermaid
graph LR
    subgraph "💾 Table Centrale"
        PC[fgp_person_core<br/>👤 NIN unique]
    end
    
    subgraph "📊 Relations 1:1"
        BIO[🔬 fgp_biometric<br/>Biométrie unique]
        E1[👶 ext_enfants]
        E2[🎓 ext_eleves]
        E3[🗳️ ext_electeurs]
        E4[👮 ext_pnc]
        E5[🎖️ ext_fardc]
        E6[🔒 ext_prison]
        E7[🏕️ ext_refugies]
        E8[🌍 ext_etrangers]
        E9[🚶 ext_deplaces]
        E10[✈️ ext_diaspora]
    end
    
    subgraph "📊 Relations 1:N"
        STRATA[📋 fgp_strata_membership<br/>Plusieurs strates possibles]
        DOCS[📄 fgp_documents<br/>Plusieurs documents]
        AUDIT[📝 fgp_audit_trail<br/>Historique complet]
        ABIS[🔍 abis_matches<br/>Correspondances biométriques]
    end
    
    PC -->|1:1| BIO
    PC -->|1:0..1| E1
    PC -->|1:0..1| E2
    PC -->|1:0..1| E3
    PC -->|1:0..1| E4
    PC -->|1:0..1| E5
    PC -->|1:0..1| E6
    PC -->|1:0..1| E7
    PC -->|1:0..1| E8
    PC -->|1:0..1| E9
    PC -->|1:0..1| E10
    
    PC -->|1:N| STRATA
    PC -->|1:N| DOCS
    PC -->|1:N| AUDIT
    PC -->|1:N| ABIS
    
    classDef central fill:#1976D2,stroke:#0D47A1,stroke-width:4px,color:#fff
    classDef oneone fill:#43A047,stroke:#2E7D32,stroke-width:2px,color:#fff
    classDef onemany fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff
    
    class PC central
    class BIO,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10 oneone
    class STRATA,DOCS,AUDIT,ABIS onemany
```

---

## 📈 STATISTIQUES DE LA BASE

```mermaid
graph TB
    Total[🗄️ BASE DE DONNÉES FGP<br/>31 Tables au total]
    
    subgraph "📊 Répartition par Catégorie"
        Core[💾 Tables Core<br/>5 tables<br/>fgp_person_core<br/>fgp_biometric<br/>fgp_strata_membership<br/>fgp_documents<br/>fgp_audit_trail]
        
        Extensions[🎯 Extensions Strates<br/>10 tables<br/>ext_enfants<br/>ext_eleves<br/>ext_electeurs<br/>ext_pnc<br/>ext_fardc<br/>ext_prison<br/>ext_refugies<br/>ext_etrangers<br/>ext_deplaces<br/>ext_diaspora]
        
        ABIS[🔍 ABIS<br/>1 table<br/>abis_matches]
        
        Enrollment[🔄 Enrollment<br/>5 tables<br/>enrollment_sessions<br/>enrollment_validations<br/>enrollment_events<br/>enrollment_receipts<br/>enrollment_statistics]
        
        Django[⚙️ Django<br/>10 tables<br/>auth_*<br/>django_*]
    end
    
    Total --> Core
    Total --> Extensions
    Total --> ABIS
    Total --> Enrollment
    Total --> Django
    
    classDef total fill:#1976D2,stroke:#0D47A1,stroke-width:4px,color:#fff,font-weight:bold
    classDef cat1 fill:#43A047,stroke:#2E7D32,stroke-width:2px,color:#fff
    classDef cat2 fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff
    classDef cat3 fill:#8E24AA,stroke:#6A1B9A,stroke-width:2px,color:#fff
    classDef cat4 fill:#00ACC1,stroke:#006064,stroke-width:2px,color:#fff
    classDef cat5 fill:#757575,stroke:#424242,stroke-width:2px,color:#fff
    
    class Total total
    class Core cat1
    class Extensions cat2
    class ABIS cat3
    class Enrollment cat4
    class Django cat5
```

---

## 🎯 LES 10 STRATES

```mermaid
graph TB
    Strates[🎯 10 STRATES OFFICIELLES]
    
    S1[👶 ENFANT<br/>Enfants mineurs<br/>Tuteur requis]
    S2[🎓 ELEVE<br/>Élèves primaire/secondaire<br/>Établissement requis]
    S3[🗳️ ELECTEUR<br/>Électeurs/Majeurs<br/>Centre de vote CENI]
    S4[👮 PNC<br/>Police Nationale<br/>Matricule + Grade]
    S5[🎖️ FARDC<br/>Forces Armées<br/>Matricule + Grade]
    S6[🔒 PRISONNIER<br/>Détenus<br/>Dossier judiciaire]
    S7[🏕️ REFUGIE<br/>Réfugiés & Apatrides<br/>Numéro HCR]
    S8[🌍 ETRANGER<br/>Étrangers en RDC<br/>Passeport + Visa]
    S9[🚶 DEPLACE<br/>Déplacés internes<br/>Lieu origine + Camp]
    S10[✈️ DIASPORA<br/>Diaspora congolaise<br/>Pays résidence]
    
    Strates --> S1
    Strates --> S2
    Strates --> S3
    Strates --> S4
    Strates --> S5
    Strates --> S6
    Strates --> S7
    Strates --> S8
    Strates --> S9
    Strates --> S10
    
    classDef title fill:#1976D2,stroke:#0D47A1,stroke-width:4px,color:#fff,font-weight:bold
    classDef strate fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff
    
    class Strates title
    class S1,S2,S3,S4,S5,S6,S7,S8,S9,S10 strate
```

---

## 🔐 SÉCURITÉ ET CONTRAINTES

```mermaid
graph TB
    Security[🔐 SÉCURITÉ & CONTRAINTES]
    
    subgraph "✅ Contraintes CHECK"
        C1[NIN Format<br/>CD-YYYY-NNNN-NNNNNNNNN]
        C2[Sexe<br/>M ou F uniquement]
        C3[10 Strates<br/>Codes validés]
        C4[Statut Membership<br/>ACTIVE/INACTIVE/SUSPENDED]
        C5[Décision ABIS<br/>HIT/NO_HIT/REVIEW]
    end
    
    subgraph "🔑 Clés Primaires"
        PK1[NIN unique<br/>20 caractères]
        PK2[UUID v4<br/>Tables système]
        PK3[Composite Keys<br/>fgp_strata_membership]
    end
    
    subgraph "🔗 Clés Étrangères"
        FK1[Toutes extensions → NIN]
        FK2[Documents → NIN]
        FK3[Audit → NIN]
        FK4[ABIS → 2x NIN]
        FK5[Validations → Session]
    end
    
    subgraph "📑 Index Performance"
        IDX1[nom, prenom<br/>Recherche rapide]
        IDX2[date_naissance<br/>Recherche par âge]
        IDX3[telephone<br/>Contact unique]
        IDX4[strate_code<br/>Filtrage strate]
        IDX5[created_at<br/>Tri temporel]
    end
    
    Security --> C1
    Security --> C2
    Security --> C3
    Security --> C4
    Security --> C5
    Security --> PK1
    Security --> PK2
    Security --> PK3
    Security --> FK1
    Security --> FK2
    Security --> FK3
    Security --> FK4
    Security --> FK5
    Security --> IDX1
    Security --> IDX2
    Security --> IDX3
    Security --> IDX4
    Security --> IDX5
    
    classDef title fill:#1976D2,stroke:#0D47A1,stroke-width:4px,color:#fff,font-weight:bold
    classDef check fill:#43A047,stroke:#2E7D32,stroke-width:2px,color:#fff
    classDef pk fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff
    classDef fk fill:#8E24AA,stroke:#6A1B9A,stroke-width:2px,color:#fff
    classDef idx fill:#00ACC1,stroke:#006064,stroke-width:2px,color:#fff
    
    class Security title
    class C1,C2,C3,C4,C5 check
    class PK1,PK2,PK3 pk
    class FK1,FK2,FK3,FK4,FK5 fk
    class IDX1,IDX2,IDX3,IDX4,IDX5 idx
```

---

**Légende des couleurs** :
- 🔵 **Bleu** : Tables centrales / Nœuds principaux
- 🟢 **Vert** : Tables système / Processus validés
- 🟠 **Orange** : Extensions / Décisions
- 🟣 **Violet** : Enrollment Gateway
- 🔴 **Rouge** : Erreurs / Rejets
- ⚫ **Gris** : Django / Infrastructure

**Symboles** :
- `1:1` = Relation One-to-One (unique)
- `1:N` = Relation One-to-Many (multiple)
- `1:0..1` = Relation optionnelle
- `→` = Dépendance directionnelle
- `↔` = Relation bidirectionnelle

