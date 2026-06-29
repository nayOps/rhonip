-- =====================================================
-- ONIP — Schéma biométrique unifié (matricule RH)
-- La biographie est dans employee_employee (migrations RH).
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS fgp_biometric (
    registration_number VARCHAR(50) PRIMARY KEY,
    photo_uri TEXT,
    photo_hash VARCHAR(64),
    photo_quality DECIMAL(3,2) CHECK (photo_quality >= 0 AND photo_quality <= 1),
    fingerprints_uri TEXT,
    fingerprints_hash VARCHAR(64),
    fingerprints_quality DECIMAL(3,2) CHECK (fingerprints_quality >= 0 AND fingerprints_quality <= 1),
    iris_uri TEXT,
    iris_hash VARCHAR(64),
    iris_quality DECIMAL(3,2) CHECK (iris_quality >= 0 AND iris_quality <= 1),
    signature_uri TEXT,
    signature_hash VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS fgp_fingerprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number VARCHAR(50) NOT NULL REFERENCES fgp_biometric(registration_number) ON DELETE CASCADE,
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
    CONSTRAINT uniq_fgp_fingerprints_matricule_position UNIQUE (registration_number, finger_position)
);

CREATE INDEX IF NOT EXISTS idx_fgp_fingerprints_matricule ON fgp_fingerprints(registration_number);
CREATE INDEX IF NOT EXISTS idx_fgp_fingerprints_position ON fgp_fingerprints(finger_position);
CREATE INDEX IF NOT EXISTS idx_fgp_fingerprints_status ON fgp_fingerprints(capture_status);

CREATE TABLE IF NOT EXISTS abis_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number_candidate VARCHAR(50) NOT NULL,
    registration_number_existing VARCHAR(50),
    match_type VARCHAR(20) NOT NULL,
    similarity_score DECIMAL(5,4) NOT NULL,
    threshold DECIMAL(5,4) NOT NULL,
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('HIT', 'NO_HIT', 'REVIEW')),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMPTZ,
    review_decision VARCHAR(20),
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_abis_matches_candidate ON abis_matches(registration_number_candidate);
CREATE INDEX IF NOT EXISTS idx_abis_matches_existing ON abis_matches(registration_number_existing);
CREATE INDEX IF NOT EXISTS idx_abis_matches_decision ON abis_matches(decision);

CREATE OR REPLACE FUNCTION update_biometric_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_fgp_biometric_updated_at ON fgp_biometric;
CREATE TRIGGER update_fgp_biometric_updated_at
    BEFORE UPDATE ON fgp_biometric
    FOR EACH ROW EXECUTE FUNCTION update_biometric_updated_at();

COMMENT ON TABLE fgp_biometric IS 'Données biométriques liées au matricule RH (registration_number)';
COMMENT ON TABLE fgp_fingerprints IS 'Empreintes digitales par matricule et position de doigt';
