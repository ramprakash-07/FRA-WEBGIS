"""
Database configuration and connection management for FRA-SENTINEL
Supports both SQLite (development) and PostGIS (production)
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import Point, Polygon
import json

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///fra_atlas.db')
USE_POSTGIS = os.getenv('USE_POSTGIS', 'false').lower() == 'true'

# Base class for models
Base = declarative_base()

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        self.is_postgis = False
        
    def connect(self):
        """Initialize database connection"""
        try:
            if USE_POSTGIS and 'postgresql' in self.database_url:
                # PostGIS configuration
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    pool_pre_ping=True,
                    connect_args={"options": "-c timezone=utc"}
                )
                self.is_postgis = True
                logger.info("Connected to PostGIS database")
            else:
                # SQLite configuration
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
                self.is_postgis = False
                logger.info("Connected to SQLite database")
            
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            self.connect()
        return self.SessionLocal()
    
    def execute_migration(self, migration_file):
        """Execute database migration"""
        try:
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            with self.engine.connect() as conn:
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                conn.commit()
            
            logger.info(f"Migration executed successfully: {migration_file}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def create_spatial_indexes(self):
        """Create spatial indexes if using PostGIS"""
        if not self.is_postgis:
            return True
        
        try:
            spatial_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_states_geometry ON states USING GIST (geometry);",
                "CREATE INDEX IF NOT EXISTS idx_districts_geometry ON districts USING GIST (geometry);",
                "CREATE INDEX IF NOT EXISTS idx_blocks_geometry ON blocks USING GIST (geometry);",
                "CREATE INDEX IF NOT EXISTS idx_villages_geometry ON villages USING GIST (geometry);",
                "CREATE INDEX IF NOT EXISTS idx_patta_holders_geometry ON patta_holders USING GIST (geometry);"
            ]
            
            with self.engine.connect() as conn:
                for index_sql in spatial_indexes:
                    conn.execute(text(index_sql))
                conn.commit()
            
            logger.info("Spatial indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Spatial index creation failed: {e}")
            return False
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency to get database session"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with migrations"""
    if not db_manager.connect():
        return False
    
    # Test connection
    if not db_manager.test_connection():
        return False
    
    # Execute migrations if using PostGIS
    if db_manager.is_postgis:
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '001_create_spatial_tables.sql')
        if os.path.exists(migration_file):
            db_manager.execute_migration(migration_file)
            db_manager.create_spatial_indexes()
    
    return True

# Spatial utility functions
def create_point(longitude, latitude, srid=4326):
    """Create a Point geometry"""
    if db_manager.is_postgis:
        return f"ST_GeomFromText('POINT({longitude} {latitude})', {srid})"
    else:
        return Point(longitude, latitude)

def create_polygon(coordinates, srid=4326):
    """Create a Polygon geometry"""
    if db_manager.is_postgis:
        coords_str = ', '.join([f"{lon} {lat}" for lon, lat in coordinates])
        return f"ST_GeomFromText('POLYGON(({coords_str}))', {srid})"
    else:
        return Polygon(coordinates)

def geometry_to_geojson(geometry):
    """Convert geometry to GeoJSON"""
    if db_manager.is_postgis:
        # For PostGIS, geometry is already a WKB
        return to_shape(geometry).__geo_interface__
    else:
        # For SQLite, geometry is stored as text
        return json.loads(geometry) if isinstance(geometry, str) else geometry

# Database models
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class State(Base):
    __tablename__ = "states"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True)
    geometry = Column(Geometry('POLYGON', srid=4326)) if USE_POSTGIS else Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    districts = relationship("District", back_populates="state")

class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True)
    state_id = Column(Integer, ForeignKey("states.id"))
    geometry = Column(Geometry('POLYGON', srid=4326)) if USE_POSTGIS else Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    state = relationship("State", back_populates="districts")
    blocks = relationship("Block", back_populates="district")

class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True)
    district_id = Column(Integer, ForeignKey("districts.id"))
    geometry = Column(Geometry('POLYGON', srid=4326)) if USE_POSTGIS else Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    district = relationship("District", back_populates="blocks")
    villages = relationship("Village", back_populates="block")

class Village(Base):
    __tablename__ = "villages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True)
    block_id = Column(Integer, ForeignKey("blocks.id"))
    geometry = Column(Geometry('POLYGON', srid=4326)) if USE_POSTGIS else Column(Text)
    centroid = Column(Geometry('POINT', srid=4326)) if USE_POSTGIS else Column(Text)
    area_hectares = Column(Float)
    population = Column(Integer)
    tribal_population_pct = Column(Float)
    forest_cover_pct = Column(Float)
    water_bodies_count = Column(Integer)
    agricultural_land_pct = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    block = relationship("Block", back_populates="villages")
    patta_holders = relationship("PattaHolder", back_populates="village")

class PattaHolder(Base):
    __tablename__ = "patta_holders"
    
    id = Column(Integer, primary_key=True)
    file_id = Column(String(50), unique=True, nullable=False)
    holder_name = Column(String(200), nullable=False)
    father_husband_name = Column(String(200))
    tribal_group = Column(String(100))
    family_size = Column(Integer)
    claim_type = Column(String(10))
    claimant_category = Column(String(10))
    village_id = Column(Integer, ForeignKey("villages.id"))
    geometry = Column(Geometry('POINT', srid=4326)) if USE_POSTGIS else Column(Text)
    area_claimed = Column(Float)
    area_vested = Column(Float)
    status = Column(String(20))
    survey_number = Column(String(100))
    dag_number = Column(String(100))
    khasra_number = Column(String(100))
    patta_number = Column(String(100))
    document_file_name = Column(String(255))
    document_file_size = Column(Integer)
    extraction_accuracy = Column(Float)
    uploaded_by = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified_by = Column(String(100))
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    village = relationship("Village", back_populates="patta_holders")

# Initialize database on import
if __name__ == "__main__":
    init_database()









