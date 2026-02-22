# Flask Health Check Endpoint for FRA-SENTINEL
# Comprehensive health monitoring for production deployment

from flask import jsonify, current_app
import psycopg2
import redis
import os
import time
from datetime import datetime

def check_database_health():
    """Check database connectivity and PostGIS availability"""
    try:
        # Get database connection details
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return {"status": "error", "message": "DATABASE_URL not configured"}
        
        # Parse database URL
        import urllib.parse as urlparse
        url = urlparse.urlparse(db_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],
            user=url.username,
            password=url.password
        )
        
        cursor = conn.cursor()
        
        # Check basic connectivity
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        # Check PostGIS extension
        cursor.execute("SELECT PostGIS_Version();")
        postgis_version = cursor.fetchone()[0]
        
        # Check database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
        db_size = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database_version": db_version,
            "postgis_version": postgis_version,
            "database_size": db_size
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_redis_health():
    """Check Redis connectivity and memory usage"""
    try:
        # Get Redis connection details
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return {"status": "error", "message": "REDIS_URL not configured"}
        
        # Connect to Redis
        r = redis.from_url(redis_url)
        
        # Test basic connectivity
        r.ping()
        
        # Get Redis info
        info = r.info()
        
        return {
            "status": "healthy",
            "redis_version": info.get('redis_version'),
            "used_memory_human": info.get('used_memory_human'),
            "connected_clients": info.get('connected_clients'),
            "uptime_in_seconds": info.get('uptime_in_seconds')
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_ocr_dependencies():
    """Check OCR and ML dependencies"""
    try:
        import tesseract
        import cv2
        import numpy as np
        from PIL import Image
        
        # Check Tesseract
        tesseract_version = tesseract.get_tesseract_version()
        
        # Check OpenCV
        cv2_version = cv2.__version__
        
        # Check NumPy
        numpy_version = np.__version__
        
        return {
            "status": "healthy",
            "tesseract_version": tesseract_version,
            "opencv_version": cv2_version,
            "numpy_version": numpy_version
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        
        # Get disk usage
        total, used, free = shutil.disk_usage("/")
        
        # Convert to GB
        total_gb = total // (1024**3)
        used_gb = used // (1024**3)
        free_gb = free // (1024**3)
        
        # Calculate percentage
        used_percent = (used / total) * 100
        
        status = "healthy" if used_percent < 90 else "warning" if used_percent < 95 else "critical"
        
        return {
            "status": status,
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "used_percent": round(used_percent, 2)
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_memory_usage():
    """Check memory usage"""
    try:
        import psutil
        
        # Get memory info
        memory = psutil.virtual_memory()
        
        status = "healthy" if memory.percent < 90 else "warning" if memory.percent < 95 else "critical"
        
        return {
            "status": status,
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_application_health():
    """Check application-specific health metrics"""
    try:
        # Check if key modules are importable
        from webgis.app import app
        from blockchain_storage import SimpleBlockchain
        
        # Check if database tables exist
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            import urllib.parse as urlparse
            url = urlparse.urlparse(db_url)
            conn = psycopg2.connect(
                host=url.hostname,
                port=url.port,
                database=url.path[1:],
                user=url.username,
                password=url.password
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        else:
            table_count = 0
        
        return {
            "status": "healthy",
            "flask_app": "loaded",
            "blockchain_module": "loaded",
            "database_tables": table_count
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.route('/api/health')
def health_check():
    """Comprehensive health check endpoint"""
    start_time = time.time()
    
    # Run all health checks
    checks = {
        "timestamp": datetime.utcnow().isoformat(),
        "application": check_application_health(),
        "database": check_database_health(),
        "redis": check_redis_health(),
        "ocr_dependencies": check_ocr_dependencies(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage()
    }
    
    # Calculate overall health status
    overall_status = "healthy"
    for check_name, check_result in checks.items():
        if check_name == "timestamp":
            continue
        if check_result.get("status") == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check_result.get("status") == "warning" and overall_status == "healthy":
            overall_status = "warning"
        elif check_result.get("status") == "critical":
            overall_status = "critical"
            break
    
    # Add response time
    response_time = round((time.time() - start_time) * 1000, 2)
    checks["response_time_ms"] = response_time
    checks["overall_status"] = overall_status
    
    # Return appropriate HTTP status code
    if overall_status == "healthy":
        return jsonify(checks), 200
    elif overall_status == "warning":
        return jsonify(checks), 200
    else:
        return jsonify(checks), 503

@app.route('/api/health/liveness')
def liveness_check():
    """Simple liveness check for Kubernetes/Docker"""
    return jsonify({"status": "alive", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route('/api/health/readiness')
def readiness_check():
    """Readiness check for Kubernetes/Docker"""
    # Check if critical services are available
    db_health = check_database_health()
    redis_health = check_redis_health()
    
    if db_health.get("status") == "healthy" and redis_health.get("status") == "healthy":
        return jsonify({"status": "ready", "timestamp": datetime.utcnow().isoformat()}), 200
    else:
        return jsonify({
            "status": "not_ready",
            "database": db_health.get("status"),
            "redis": redis_health.get("status"),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


