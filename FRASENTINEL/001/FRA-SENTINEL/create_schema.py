"""
Database Schema Creation for FRA-SENTINEL
Creates all necessary tables for the application
"""

import sqlite3
import os

def create_database_schema():
    """Create database schema"""
    
    # Remove existing database if it exists
    if os.path.exists('fra_atlas.db'):
        os.remove('fra_atlas.db')
    
    conn = sqlite3.connect('fra_atlas.db')
    cursor = conn.cursor()
    
    try:
        # Create states table
        cursor.execute("""
            CREATE TABLE states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(10) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create districts table
        cursor.execute("""
            CREATE TABLE districts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) UNIQUE,
                state_id INTEGER REFERENCES states(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create blocks table
        cursor.execute("""
            CREATE TABLE blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) UNIQUE,
                district_id INTEGER REFERENCES districts(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create villages table
        cursor.execute("""
            CREATE TABLE villages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(10) UNIQUE,
                block_id INTEGER REFERENCES blocks(id),
                population INTEGER,
                tribal_population_pct DECIMAL(5,2),
                forest_cover_pct DECIMAL(5,2),
                water_bodies_count INTEGER,
                agricultural_land_pct DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create patta holders table
        cursor.execute("""
            CREATE TABLE patta_holders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id VARCHAR(50) UNIQUE NOT NULL,
                holder_name VARCHAR(200) NOT NULL,
                father_husband_name VARCHAR(200),
                tribal_group VARCHAR(100),
                family_size INTEGER,
                claim_type VARCHAR(10) CHECK (claim_type IN ('IFR', 'CR', 'CFR')),
                claimant_category VARCHAR(10) CHECK (claimant_category IN ('ST', 'OTFD')),
                village_id INTEGER REFERENCES villages(id),
                geometry TEXT,
                area_claimed DECIMAL(10,4),
                area_vested DECIMAL(10,4),
                status VARCHAR(20) CHECK (status IN ('filed', 'under_verification', 'granted', 'rejected', 'appealed')),
                survey_number VARCHAR(100),
                dag_number VARCHAR(100),
                khasra_number VARCHAR(100),
                patta_number VARCHAR(100),
                document_file_name VARCHAR(255),
                document_file_size INTEGER,
                extraction_accuracy DECIMAL(5,2),
                uploaded_by VARCHAR(100),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_by VARCHAR(100),
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create progress tracking table
        cursor.execute("""
            CREATE TABLE progress_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                village_id INTEGER REFERENCES villages(id),
                quarter VARCHAR(10) NOT NULL,
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
            )
        """)
        
        # Create asset mapping results table
        cursor.execute("""
            CREATE TABLE asset_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                village_id INTEGER REFERENCES villages(id),
                model_version VARCHAR(50) NOT NULL,
                classification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                farmland_pct DECIMAL(5,2),
                forest_pct DECIMAL(5,2),
                water_pct DECIMAL(5,2),
                homestead_pct DECIMAL(5,2),
                confidence_score DECIMAL(5,2),
                total_pixels INTEGER,
                geometry TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create DSS recommendations table
        cursor.execute("""
            CREATE TABLE dss_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                reasons TEXT,
                recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create processing queue table
        cursor.execute("""
            CREATE TABLE processing_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id VARCHAR(50) UNIQUE NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                status VARCHAR(20) CHECK (status IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                error_message TEXT,
                processing_started_at TIMESTAMP,
                processing_completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_districts_state_id ON districts (state_id)")
        cursor.execute("CREATE INDEX idx_blocks_district_id ON blocks (district_id)")
        cursor.execute("CREATE INDEX idx_villages_block_id ON villages (block_id)")
        cursor.execute("CREATE INDEX idx_patta_holders_village_id ON patta_holders (village_id)")
        cursor.execute("CREATE INDEX idx_patta_holders_status ON patta_holders (status)")
        cursor.execute("CREATE INDEX idx_patta_holders_claim_type ON patta_holders (claim_type)")
        cursor.execute("CREATE INDEX idx_progress_tracking_village_id ON progress_tracking (village_id)")
        cursor.execute("CREATE INDEX idx_progress_tracking_quarter ON progress_tracking (quarter, year)")
        cursor.execute("CREATE INDEX idx_asset_mapping_village_id ON asset_mapping (village_id)")
        cursor.execute("CREATE INDEX idx_dss_recommendations_village_id ON dss_recommendations (village_id)")
        cursor.execute("CREATE INDEX idx_processing_queue_status ON processing_queue (status)")
        cursor.execute("CREATE INDEX idx_processing_queue_priority ON processing_queue (priority)")
        
        conn.commit()
        print("Database schema created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating database schema: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_database_schema()









