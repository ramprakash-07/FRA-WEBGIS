# FRA-SENTINEL Deployment Runbook

## Quick Start Guide

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 50GB disk space

### 1. Clone and Setup
```bash
git clone <repository-url>
cd FRA-SENTINEL
pip install -r requirements_enhanced.txt
```

### 2. Database Setup
```bash
# Create database schema
python create_schema.py

# Seed with sample data
python demo_data.py
```

### 3. Run Application
```bash
# Development mode
python webgis/enhanced_app.py

# Production mode with Docker
docker-compose up -d
```

### 4. Access Application
- **Dashboard**: http://localhost:5000
- **WebGIS Atlas**: http://localhost:5000/atlas
- **Admin Panel**: http://localhost:5000/admin
- **API Health**: http://localhost:5000/api/health

## Production Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### Database Migration (PostGIS)
```bash
# Run migrations
docker-compose exec web python -m flask db upgrade

# Seed production data
docker-compose exec web python demo_data.py
```

## API Usage Examples

### 1. Upload and Process Documents
```bash
# Single file upload
curl -X POST http://localhost:5000/api/upload \
  -F "file=@sample_patta.pdf"

# Batch upload
curl -X POST http://localhost:5000/api/batch-upload \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf"
```

### 2. DSS Analysis
```bash
# Analyze village
curl -X POST http://localhost:5000/api/dss/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "village_id": 1,
    "village_data": {
      "name": "Khargone",
      "population": 500,
      "tribal_population_pct": 60,
      "forest_cover_pct": 45,
      "water_bodies_count": 1,
      "agricultural_land_pct": 55
    }
  }'
```

### 3. Get Spatial Data
```bash
# Get villages
curl http://localhost:5000/api/villages

# Get patta holders
curl http://localhost:5000/api/patta-holders?village_id=1&claim_type=IFR

# Get progress data
curl http://localhost:5000/api/progress
```

### 4. Map Tiles
```bash
# Get map tile
curl http://localhost:5000/api/tiles/ifr/10/500/300.png

# Generate tiles for layer
curl -X POST http://localhost:5000/api/generate-tiles \
  -H "Content-Type: application/json" \
  -d '{"layer": "ifr", "min_zoom": 1, "max_zoom": 10}'
```

## Monitoring and Maintenance

### Health Checks
```bash
# System health
curl http://localhost:5000/api/health

# Queue statistics
curl http://localhost:5000/api/queue/stats

# Model information
curl http://localhost:5000/api/models
```

### Log Monitoring
```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# All services
docker-compose logs -f
```

### Performance Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **MLflow**: http://localhost:5001

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check database status
docker-compose exec db psql -U fra_user -d fra_atlas -c "SELECT 1"

# Restart database
docker-compose restart db
```

#### 2. OCR Processing Fails
```bash
# Check Tesseract installation
docker-compose exec web tesseract --version

# Verify file permissions
docker-compose exec web ls -la uploads/
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
```

#### 4. Tile Generation Slow
```bash
# Check tile cache
docker-compose exec web ls -la cache/

# Clear cache
docker-compose exec web rm -rf cache/*
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Check slow queries
EXPLAIN ANALYZE SELECT * FROM patta_holders WHERE village_id = 1;

-- Add indexes
CREATE INDEX idx_patta_holders_village_status ON patta_holders(village_id, status);
```

#### 2. Application Optimization
```bash
# Enable gunicorn workers
docker-compose exec web gunicorn --workers 4 --worker-class gevent webgis.app:app

# Enable Redis caching
export REDIS_URL=redis://redis:6379/0
```

#### 3. ML Model Optimization
```bash
# Retrain models with more data
docker-compose exec web python -c "
from webgis.models import retrain_dss_models
retrain_dss_models(training_data)
"
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U fra_user fra_atlas > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U fra_user fra_atlas < backup_20240127.sql
```

### File Backup
```bash
# Backup uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/
```

### Full System Backup
```bash
# Backup entire application
docker-compose exec web tar -czf /app/fra_sentinel_backup_$(date +%Y%m%d).tar.gz \
  /app/data /app/models /app/uploads /app/logs
```

## Security Hardening

### 1. Environment Security
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env file
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://fra_user:secure_password@db:5432/fra_atlas
```

### 2. Network Security
```yaml
# docker-compose.yml
services:
  web:
    networks:
      - internal
  db:
    networks:
      - internal
    ports: []  # Remove external port exposure
```

### 3. File Security
```bash
# Set proper file permissions
chmod 600 .env
chmod 755 uploads/
chmod 700 models/
```

## Scaling Guidelines

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3
    environment:
      - WORKER_PROCESSES=4
```

### Database Scaling
```bash
# Read replicas
docker-compose exec db psql -c "CREATE REPLICATION USER replica_user;"

# Connection pooling
pip install pgbouncer
```

### Load Balancing
```nginx
# nginx.conf
upstream fra_backend {
    server web1:5000;
    server web2:5000;
    server web3:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://fra_backend;
    }
}
```

## Support and Maintenance

### Regular Maintenance Tasks
1. **Daily**: Check system health and logs
2. **Weekly**: Database maintenance and cleanup
3. **Monthly**: Model retraining and updates
4. **Quarterly**: Security updates and patches

### Contact Information
- **Technical Support**: support@fra-sentinel.gov.in
- **Documentation**: https://docs.fra-sentinel.gov.in
- **Issue Tracker**: https://github.com/fra-sentinel/issues

### Version Updates
```bash
# Check for updates
git fetch origin
git log HEAD..origin/main

# Apply updates
git pull origin main
docker-compose build
docker-compose up -d
```

This runbook provides comprehensive guidance for deploying, operating, and maintaining the FRA-SENTINEL system in production environments.









