-- FRA-SENTINEL Database Migration 001
-- Create spatial tables with PostGIS support
-- Migration: 001_create_spatial_tables.sql
-- Created: 2025-01-27
-- Description: Initial spatial database schema for FRA Atlas

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create spatial reference systems for India
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
VALUES (
    4326, 'EPSG', 4326, 
    '+proj=longlat +datum=WGS84 +no_defs',
    'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
) ON CONFLICT (srid) DO NOTHING;

-- States table
CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) UNIQUE,
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Districts table
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    state_id INTEGER REFERENCES states(id),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blocks table
CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    district_id INTEGER REFERENCES districts(id),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Villages table
CREATE TABLE IF NOT EXISTS villages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    block_id INTEGER REFERENCES blocks(id),
    geometry GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    area_hectares DECIMAL(10,4),
    population INTEGER,
    tribal_population_pct DECIMAL(5,2),
    forest_cover_pct DECIMAL(5,2),
    water_bodies_count INTEGER,
    agricultural_land_pct DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patta holders table
CREATE TABLE IF NOT EXISTS patta_holders (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(50) UNIQUE NOT NULL,
    holder_name VARCHAR(200) NOT NULL,
    father_husband_name VARCHAR(200),
    tribal_group VARCHAR(100),
    family_size INTEGER,
    claim_type VARCHAR(10) CHECK (claim_type IN ('IFR', 'CR', 'CFR')),
    claimant_category VARCHAR(10) CHECK (claimant_category IN ('ST', 'OTFD')),
    village_id INTEGER REFERENCES villages(id),
    geometry GEOMETRY(POINT, 4326),
    area_claimed DECIMAL(10,4),
    area_vested DECIMAL(10,4),
    status VARCHAR(20) CHECK (status IN ('filed', 'under_verification', 'granted', 'rejected', 'appealed')),
    survey_number VARCHAR(100),
    dag_number VARCHAR(100),
    khasra_number VARCHAR(100),
    patta_number VARCHAR(100),
    document_file_name VARCHAR(255),
    document_file_size BIGINT,
    extraction_accuracy DECIMAL(5,2),
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress tracking table
CREATE TABLE IF NOT EXISTS progress_tracking (
    id SERIAL PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id),
    quarter VARCHAR(10) NOT NULL, -- Format: YYYY-Q1/Q2/Q3/Q4
    year INTEGER NOT NULL,
    ifr_filed INTEGER DEFAULT 0,
    ifr_granted INTEGER DEFAULT 0,
    ifr_rejected INTEGER DEFAULT 0,
    cr_filed INTEGER DEFAULT 0,
    cr_granted INTEGER DEFAULT 0,
    cr_rejected INTEGER DEFAULT 0,
    cfr_filed INTEGER DEFAULT 0,
    cfr_granted INTEGER DEFAULT 0,
    cfr_rejected INTEGER DEFAULT 0,
    total_area_vested DECIMAL(10,4) DEFAULT 0,
    cfr_managed_area DECIMAL(10,4) DEFAULT 0,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(village_id, quarter, year)
);

-- Asset mapping results table
CREATE TABLE IF NOT EXISTS asset_mapping (
    id SERIAL PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id),
    model_version VARCHAR(50) NOT NULL,
    classification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    farmland_pct DECIMAL(5,2),
    forest_pct DECIMAL(5,2),
    water_pct DECIMAL(5,2),
    homestead_pct DECIMAL(5,2),
    confidence_score DECIMAL(5,2),
    total_pixels INTEGER,
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DSS recommendations table
CREATE TABLE IF NOT EXISTS dss_recommendations (
    id SERIAL PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id),
    scheme_key VARCHAR(50) NOT NULL,
    scheme_name VARCHAR(200) NOT NULL,
    ministry VARCHAR(200),
    category VARCHAR(100),
    eligibility_score DECIMAL(5,2),
    priority VARCHAR(20) CHECK (priority IN ('High', 'Medium', 'Low')),
    beneficiaries_estimate INTEGER,
    benefit_amount VARCHAR(100),
    convergence_score DECIMAL(5,2),
    reasons TEXT[],
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document processing queue table
CREATE TABLE IF NOT EXISTS processing_queue (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(50) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial indexes
CREATE INDEX IF NOT EXISTS idx_states_geometry ON states USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_districts_geometry ON districts USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_blocks_geometry ON blocks USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_villages_geometry ON villages USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_villages_centroid ON villages USING GIST (centroid);
CREATE INDEX IF NOT EXISTS idx_patta_holders_geometry ON patta_holders USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_asset_mapping_geometry ON asset_mapping USING GIST (geometry);

-- Create regular indexes
CREATE INDEX IF NOT EXISTS idx_districts_state_id ON districts (state_id);
CREATE INDEX IF NOT EXISTS idx_blocks_district_id ON blocks (district_id);
CREATE INDEX IF NOT EXISTS idx_villages_block_id ON villages (block_id);
CREATE INDEX IF NOT EXISTS idx_patta_holders_village_id ON patta_holders (village_id);
CREATE INDEX IF NOT EXISTS idx_patta_holders_status ON patta_holders (status);
CREATE INDEX IF NOT EXISTS idx_patta_holders_claim_type ON patta_holders (claim_type);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_village_id ON progress_tracking (village_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_quarter ON progress_tracking (quarter, year);
CREATE INDEX IF NOT EXISTS idx_asset_mapping_village_id ON asset_mapping (village_id);
CREATE INDEX IF NOT EXISTS idx_dss_recommendations_village_id ON dss_recommendations (village_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_status ON processing_queue (status);
CREATE INDEX IF NOT EXISTS idx_processing_queue_priority ON processing_queue (priority);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_states_updated_at BEFORE UPDATE ON states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_districts_updated_at BEFORE UPDATE ON districts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_blocks_updated_at BEFORE UPDATE ON blocks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_villages_updated_at BEFORE UPDATE ON villages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patta_holders_updated_at BEFORE UPDATE ON patta_holders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_progress_tracking_updated_at BEFORE UPDATE ON progress_tracking FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_processing_queue_updated_at BEFORE UPDATE ON processing_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO states (name, code) VALUES 
('Madhya Pradesh', 'MP'),
('Odisha', 'OR'),
('Tripura', 'TR'),
('Telangana', 'TS')
ON CONFLICT (name) DO NOTHING;

-- Migration completed
INSERT INTO schema_migrations (version, applied_at) VALUES ('001', CURRENT_TIMESTAMP) ON CONFLICT (version) DO NOTHING;









