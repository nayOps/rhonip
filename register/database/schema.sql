-- =====================================================
-- FGP - Fichier Général de la Population
-- Schéma de Base de Données - RDC
-- =====================================================

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. FGP CORE - Noyau (27 variables obligatoires)
-- =====================================================

CREATE TABLE fgp_person_core (
    -- Identifiant unique
    nin VARCHAR(20) PRIMARY KEY,
    
    -- Variables d'identité (27 du décret)
    nom TEXT NOT NULL,
    postnom TEXT,
    prenom TEXT NOT NULL,
    sexe CHAR(1) CHECK (sexe IN ('M', 'F')) NOT NULL,
    
    -- Informations de naissance
    date_naissance DATE NOT NULL,
    lieu_naissance TEXT NOT NULL,
    province_naissance TEXT NOT NULL,
    nationalite TEXT NOT NULL DEFAULT 'Congolaise',
    
    -- Statut matrimonial
    statut_matrimonial VARCHAR(20) CHECK (statut_matrimonial IN ('Célibataire', 'Marié(e)', 'Divorcé(e)', 'Veuf(ve)', 'Union libre')),
    
    -- Parents
    nom_pere TEXT,
    nom_mere TEXT,
    
    -- Adresse actuelle
    province_residence TEXT NOT NULL,
    territoire_residence TEXT,
    commune_residence TEXT,
    quartier_residence TEXT,
    avenue_residence TEXT,
    numero_residence TEXT,
    
    -- Contact
    telephone VARCHAR(20),
    email VARCHAR(255),
    
    -- Profession et éducation
    profession TEXT,
    niveau_etude VARCHAR(50),
    
    -- Pièce d'identité
    type_piece_identite VARCHAR(50),
    numero_piece_identite VARCHAR(50),
    date_emission_piece DATE,
    lieu_emission_piece TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    version INTEGER DEFAULT 1,
    
    -- Index pour performance
    CONSTRAINT fgp_person_core_nin_format CHECK (nin ~ '^CD-[0-9]{4}-[0-9]{4}-[0-9]{7}$')
);

-- Index pour recherche
CREATE INDEX idx_fgp_person_core_nom ON fgp_person_core(nom);
CREATE INDEX idx_fgp_person_core_prenom ON fgp_person_core(prenom);
CREATE INDEX idx_fgp_person_core_date_naissance ON fgp_person_core(date_naissance);
CREATE INDEX idx_fgp_person_core_province ON fgp_person_core(province_residence);
CREATE INDEX idx_fgp_person_core_telephone ON fgp_person_core(telephone);

-- =====================================================
-- 2. BIOMÉTRIE
-- =====================================================

CREATE TABLE fgp_biometric (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nin VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    -- Photo faciale
    photo_uri TEXT,
    photo_hash VARCHAR(64),
    photo_quality DECIMAL(3,2) CHECK (photo_quality >= 0 AND photo_quality <= 1),
    
    -- Empreintes digitales
    fingerprints_uri TEXT,
    fingerprints_hash VARCHAR(64),
    fingerprints_quality DECIMAL(3,2) CHECK (fingerprints_quality >= 0 AND fingerprints_quality <= 1),
    
    -- Iris (optionnel)
    iris_uri TEXT,
    iris_hash VARCHAR(64),
    iris_quality DECIMAL(3,2) CHECK (iris_quality >= 0 AND iris_quality <= 1),
    
    -- Signature
    signature_uri TEXT,
    signature_hash VARCHAR(64),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    
    UNIQUE(nin)
);

CREATE TABLE fgp_fingerprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nin VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    finger_position VARCHAR(20) NOT NULL,
    capture_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    image_uri TEXT,
    image_hash VARCHAR(64),
    template_uri TEXT,
    template_hash VARCHAR(64),
    template_format VARCHAR(30),
    quality_score DECIMAL(5,2),
    nfiq_score INTEGER,
    device VARCHAR(100),
    captured_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uniq_fgp_fingerprints_nin_position UNIQUE (nin, finger_position)
);

CREATE INDEX idx_fgp_fingerprints_nin ON fgp_fingerprints(nin);
CREATE INDEX idx_fgp_fingerprints_position ON fgp_fingerprints(finger_position);
CREATE INDEX idx_fgp_fingerprints_status ON fgp_fingerprints(capture_status);

-- =====================================================
-- 3. APPARTENANCE AUX STRATES
-- =====================================================

CREATE TABLE fgp_strata_membership (
    id UUID DEFAULT uuid_generate_v4(),
    nin VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    strate_code VARCHAR(20) NOT NULL CHECK (strate_code IN (
        'ENFANT', 'ELEVE', 'ELECTEUR', 'PNC', 'FARDC', 
        'PRISONNIER', 'REFUGIE', 'DEPLACE', 'ETRANGER', 'DIASPORA'
    )),
    valid_from DATE NOT NULL,
    valid_to DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    
    PRIMARY KEY (nin, strate_code, valid_from)
);

-- Index pour recherche par strate
CREATE INDEX idx_fgp_strata_membership_strate ON fgp_strata_membership(strate_code);
CREATE INDEX idx_fgp_strata_membership_status ON fgp_strata_membership(status);

-- =====================================================
-- 4. EXTENSIONS PAR STRATE
-- =====================================================

-- 4.1 Extension ÉLÈVES
CREATE TABLE ext_eleves (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    matricule_scolaire VARCHAR(50) UNIQUE NOT NULL,
    etablissement TEXT NOT NULL,
    code_etablissement VARCHAR(20),
    niveau VARCHAR(50) NOT NULL,
    cycle VARCHAR(20),
    annee_scolaire VARCHAR(10) NOT NULL,
    section VARCHAR(50),
    statut_scolaire VARCHAR(20) DEFAULT 'public' CHECK (statut_scolaire IN ('public', 'privé', 'régulier', 'redoublant')),
    
    -- Tuteur
    responsable_tuteur TEXT,
    contact_tuteur VARCHAR(20),
    lien_tuteur VARCHAR(30),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.2 Extension ÉLECTEURS
CREATE TABLE ext_electeurs (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    centre_vote TEXT NOT NULL,
    code_centre_vote VARCHAR(20) NOT NULL,
    circonscription TEXT NOT NULL,
    secteur_vote TEXT NOT NULL,
    statut_inscription VARCHAR(20) DEFAULT 'inscrit' CHECK (statut_inscription IN ('inscrit', 'radié', 'en_attente')),
    date_inscription_ceni DATE NOT NULL,
    bureau_vote VARCHAR(20),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.4 Extension PNC (Police)
CREATE TABLE ext_pnc (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    matricule_pnc VARCHAR(20) UNIQUE NOT NULL,
    grade VARCHAR(50) NOT NULL,
    unite TEXT NOT NULL,
    fonction TEXT,
    date_integration DATE NOT NULL,
    statut_service VARCHAR(20) DEFAULT 'actif' CHECK (statut_service IN ('actif', 'suspendu', 'retraité')),
    zone_affectation TEXT,
    type_arme VARCHAR(100),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.5 Extension FARDC (Armée)
CREATE TABLE ext_fardc (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    matricule_fardc VARCHAR(20) UNIQUE NOT NULL,
    grade VARCHAR(50) NOT NULL,
    unite_affectation TEXT NOT NULL,
    zone_operation TEXT,
    fonction TEXT,
    date_integration DATE NOT NULL,
    statut_militaire VARCHAR(20) DEFAULT 'actif' CHECK (statut_militaire IN ('actif', 'réserviste', 'blessé')),
    type_mission VARCHAR(20) CHECK (type_mission IN ('interne', 'externe')),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.6 Extension PRISONNIERS
CREATE TABLE ext_prison (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    numero_dossier_judiciaire VARCHAR(50) UNIQUE NOT NULL,
    centre_detention TEXT NOT NULL,
    statut_detention VARCHAR(30) NOT NULL CHECK (statut_detention IN ('préventif', 'condamné', 'liberté_conditionnelle')),
    date_incarceration DATE NOT NULL,
    date_liberation_prevue DATE,
    infraction TEXT,
    autorite_judiciaire TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.7 Extension RÉFUGIÉS
CREATE TABLE ext_refugies (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    numero_hcr VARCHAR(30) UNIQUE,
    pays_origine TEXT NOT NULL,
    statut_juridique VARCHAR(30) NOT NULL CHECK (statut_juridique IN ('réfugié', 'demandeur_asile', 'apatride')),
    document_sejour VARCHAR(50),
    date_entree_territoire DATE NOT NULL,
    camp_refugie TEXT,
    organisme_encadrement VARCHAR(50),
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.8 Extension ENFANTS
CREATE TABLE ext_enfants (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    tuteur_nom TEXT NOT NULL,
    tuteur_nin VARCHAR(20),
    lien_tuteur VARCHAR(30) NOT NULL,
    adresse_tuteur TEXT,
    document_parentalite VARCHAR(50),
    autorisation_parentale BOOLEAN DEFAULT TRUE,
    structure_accueil TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.9 Extension ÉTRANGERS
CREATE TABLE ext_etrangers (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    -- Champs obligatoires
    pays_origine TEXT NOT NULL,
    numero_passeport VARCHAR(50) NOT NULL,
    
    -- Informations passeport
    ville_delivrance TEXT,
    date_delivrance DATE,
    date_expiration DATE,
    
    -- Visa/Permis de séjour
    numero_visa_permis VARCHAR(50),
    date_visa DATE,
    type_sejour VARCHAR(50) CHECK (type_sejour IN ('Temporaire', 'Permanent', 'Transit', 'Diplomatique', 'Autre')),
    
    -- Résidence en RDC
    adresse_residence_rdc TEXT,
    profession_rdc TEXT,
    employeur_organisation TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.10 Extension DÉPLACÉS INTERNES
CREATE TABLE ext_deplaces (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    -- Tous les champs sont optionnels pour le moment
    lieu_origine TEXT,
    province_origine TEXT,
    territoire_origine TEXT,
    raison_deplacement TEXT,
    date_deplacement DATE,
    site_camp_deplaces TEXT,
    numero_carte_deplace VARCHAR(50),
    organisme_assistance VARCHAR(100),
    type_hebergement VARCHAR(50),
    chef_menage_nin VARCHAR(20),
    situation_sanitaire TEXT,
    besoins_prioritaires TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- 4.11 Extension DIASPORA
CREATE TABLE ext_diaspora (
    nin VARCHAR(20) PRIMARY KEY REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    
    -- Tous les champs sont optionnels pour le moment
    pays_residence_actuelle TEXT,
    ville_residence TEXT,
    date_depart_rdc DATE,
    type_residence VARCHAR(50) CHECK (type_residence IN ('Permanent', 'Temporaire', 'Étudiant', 'Travailleur', 'Autre')),
    document_etranger VARCHAR(100),
    numero_document_etranger VARCHAR(50),
    profession_etranger TEXT,
    employeur_etranger TEXT,
    souhait_retour BOOLEAN DEFAULT FALSE,
    date_retour_prevue DATE,
    representation_consulaire TEXT,
    ville_consulat TEXT,
    statut_legal_etranger VARCHAR(50),
    double_nationalite BOOLEAN DEFAULT FALSE,
    pays_autre_nationalite TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- =====================================================
-- 5. AUDIT TRAIL
-- =====================================================

CREATE TABLE fgp_audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nin VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, VIEW
    table_name VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(100) NOT NULL,
    user_ip INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_audit_trail_nin ON fgp_audit_trail(nin);
CREATE INDEX idx_audit_trail_action ON fgp_audit_trail(action);
CREATE INDEX idx_audit_trail_timestamp ON fgp_audit_trail(timestamp);

-- =====================================================
-- 6. DOCUMENTS ET PIÈCES JOINTES
-- =====================================================

CREATE TABLE fgp_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nin VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- 'acte_naissance', 'carte_identite', 'diplome', etc.
    document_uri TEXT NOT NULL,
    document_hash VARCHAR(64) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMPTZ,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- Index pour performance
CREATE INDEX idx_documents_nin ON fgp_documents(nin);
CREATE INDEX idx_documents_type ON fgp_documents(document_type);

-- =====================================================
-- 7. ABIS - Système de Déduplication Biométrique
-- =====================================================

CREATE TABLE abis_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nin_candidate VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    nin_existing VARCHAR(20) REFERENCES fgp_person_core(nin) ON DELETE CASCADE,
    match_type VARCHAR(20) NOT NULL, -- 'face', 'fingerprint', 'iris'
    similarity_score DECIMAL(5,4) NOT NULL,
    threshold DECIMAL(5,4) NOT NULL,
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('HIT', 'NO_HIT', 'REVIEW')),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ,
    review_decision VARCHAR(20),
    review_notes TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_abis_matches_candidate ON abis_matches(nin_candidate);
CREATE INDEX idx_abis_matches_existing ON abis_matches(nin_existing);
CREATE INDEX idx_abis_matches_decision ON abis_matches(decision);

-- =====================================================
-- 8. FONCTIONS ET TRIGGERS
-- =====================================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_fgp_person_core_updated_at BEFORE UPDATE ON fgp_person_core FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fgp_biometric_updated_at BEFORE UPDATE ON fgp_biometric FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_eleves_updated_at BEFORE UPDATE ON ext_eleves FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_electeurs_updated_at BEFORE UPDATE ON ext_electeurs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_pnc_updated_at BEFORE UPDATE ON ext_pnc FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_fardc_updated_at BEFORE UPDATE ON ext_fardc FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_prison_updated_at BEFORE UPDATE ON ext_prison FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_refugies_updated_at BEFORE UPDATE ON ext_refugies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_enfants_updated_at BEFORE UPDATE ON ext_enfants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_etrangers_updated_at BEFORE UPDATE ON ext_etrangers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_deplaces_updated_at BEFORE UPDATE ON ext_deplaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ext_diaspora_updated_at BEFORE UPDATE ON ext_diaspora FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 9. VUES UTILES
-- =====================================================

-- Vue pour obtenir toutes les informations d'une personne
CREATE VIEW v_person_complete AS
SELECT 
    p.*,
    b.photo_uri, b.photo_quality,
    b.fingerprints_uri, b.fingerprints_quality,
    b.iris_uri, b.iris_quality,
    b.signature_uri,
    STRING_AGG(s.strate_code, ', ') as strates
FROM fgp_person_core p
LEFT JOIN fgp_biometric b ON p.nin = b.nin
LEFT JOIN fgp_strata_membership s ON p.nin = s.nin AND s.status = 'ACTIVE'
GROUP BY p.nin, b.photo_uri, b.photo_quality, b.fingerprints_uri, b.fingerprints_quality, 
         b.iris_uri, b.iris_quality, b.signature_uri;

-- =====================================================
-- 10. COMMENTAIRES
-- =====================================================

COMMENT ON TABLE fgp_person_core IS 'Table principale contenant les 27 variables obligatoires du FGP';
COMMENT ON TABLE fgp_biometric IS 'Données biométriques (photo, empreintes, iris)';
COMMENT ON TABLE fgp_strata_membership IS 'Appartenance aux différentes strates';
COMMENT ON TABLE fgp_audit_trail IS 'Traçabilité complète des opérations';
COMMENT ON TABLE abis_matches IS 'Résultats de déduplication biométrique';

-- =====================================================
-- FIN DU SCHÉMA
-- =====================================================
