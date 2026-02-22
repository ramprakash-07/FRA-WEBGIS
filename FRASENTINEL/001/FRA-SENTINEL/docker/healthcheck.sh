# Health Check Script for FRA-SENTINEL
# Comprehensive health monitoring for all services

#!/bin/bash

# =============================================================================
# Health Check Configuration
# =============================================================================
set -e

# Service endpoints
BACKEND_URL="http://localhost:5000"
DB_HOST="db"
DB_PORT="5432"
REDIS_HOST="redis"
REDIS_PORT="6379"

# Health check timeout
TIMEOUT=10

# =============================================================================
# Database Health Check
# =============================================================================
check_database() {
    echo "🔍 Checking database connection..."
    
    # Check if PostgreSQL is accepting connections
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
        echo "✅ Database connection: OK"
        
        # Check if PostGIS extension is available
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT PostGIS_Version();" >/dev/null 2>&1; then
            echo "✅ PostGIS extension: OK"
        else
            echo "❌ PostGIS extension: FAILED"
            return 1
        fi
    else
        echo "❌ Database connection: FAILED"
        return 1
    fi
}

# =============================================================================
# Redis Health Check
# =============================================================================
check_redis() {
    echo "🔍 Checking Redis connection..."
    
    # Check if Redis is accepting connections
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" ping >/dev/null 2>&1; then
        echo "✅ Redis connection: OK"
        
        # Check Redis memory usage
        MEMORY_USAGE=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        echo "📊 Redis memory usage: $MEMORY_USAGE"
    else
        echo "❌ Redis connection: FAILED"
        return 1
    fi
}

# =============================================================================
# Backend Health Check
# =============================================================================
check_backend() {
    echo "🔍 Checking backend service..."
    
    # Check if backend is responding
    if curl -f -s --max-time "$TIMEOUT" "$BACKEND_URL/api/health" >/dev/null 2>&1; then
        echo "✅ Backend service: OK"
        
        # Get detailed health information
        HEALTH_RESPONSE=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL/api/health")
        echo "📊 Backend health: $HEALTH_RESPONSE"
    else
        echo "❌ Backend service: FAILED"
        return 1
    fi
}

# =============================================================================
# OCR Dependencies Check
# =============================================================================
check_ocr_dependencies() {
    echo "🔍 Checking OCR dependencies..."
    
    # Check Tesseract installation
    if command -v tesseract >/dev/null 2>&1; then
        TESSERACT_VERSION=$(tesseract --version | head -n1)
        echo "✅ Tesseract OCR: $TESSERACT_VERSION"
    else
        echo "❌ Tesseract OCR: NOT INSTALLED"
        return 1
    fi
    
    # Check GDAL installation
    if command -v gdalinfo >/dev/null 2>&1; then
        GDAL_VERSION=$(gdalinfo --version)
        echo "✅ GDAL: $GDAL_VERSION"
    else
        echo "❌ GDAL: NOT INSTALLED"
        return 1
    fi
}

# =============================================================================
# Disk Space Check
# =============================================================================
check_disk_space() {
    echo "🔍 Checking disk space..."
    
    # Check available disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 90 ]; then
        echo "✅ Disk space: OK ($DISK_USAGE% used)"
    else
        echo "⚠️ Disk space: WARNING ($DISK_USAGE% used)"
    fi
}

# =============================================================================
# Memory Check
# =============================================================================
check_memory() {
    echo "🔍 Checking memory usage..."
    
    # Check available memory
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -lt 90 ]; then
        echo "✅ Memory usage: OK ($MEMORY_USAGE% used)"
    else
        echo "⚠️ Memory usage: WARNING ($MEMORY_USAGE% used)"
    fi
}

# =============================================================================
# Main Health Check Function
# =============================================================================
main() {
    echo "🏥 FRA-SENTINEL Health Check Starting..."
    echo "=========================================="
    
    # Initialize exit code
    EXIT_CODE=0
    
    # Run all health checks
    check_database || EXIT_CODE=1
    echo ""
    
    check_redis || EXIT_CODE=1
    echo ""
    
    check_backend || EXIT_CODE=1
    echo ""
    
    check_ocr_dependencies || EXIT_CODE=1
    echo ""
    
    check_disk_space
    echo ""
    
    check_memory
    echo ""
    
    # Final status
    if [ $EXIT_CODE -eq 0 ]; then
        echo "🎉 All health checks passed!"
    else
        echo "❌ Some health checks failed!"
    fi
    
    echo "=========================================="
    exit $EXIT_CODE
}

# =============================================================================
# Run main function
# =============================================================================
main "$@"
