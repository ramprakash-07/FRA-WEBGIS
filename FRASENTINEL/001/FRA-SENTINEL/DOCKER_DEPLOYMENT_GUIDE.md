# Docker Deployment Guide for FRA-SENTINEL
# Complete setup for Railway.app, AWS Lightsail, EC2

## 🚀 Quick Start Commands

### 1. **Development Setup**
```bash
# Clone and navigate to project
git clone <your-repo>
cd FRA-SENTINEL

# Copy environment variables
cp env.example .env
# Edit .env with your configuration

# Start development environment
docker-compose -f docker-compose.production.yml up --build
```

### 2. **Production Deployment**
```bash
# Build and start production services
docker-compose -f docker-compose.production.yml up -d --build

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│  Flask Backend  │────│   PostgreSQL    │
│   Port: 80      │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│     Redis       │──────────────┘
                        │   Port: 6379    │
                        └─────────────────┘
```

## 📋 Service Details

### **Backend Service (Flask)**
- **Port**: 5000
- **Framework**: Flask with Gunicorn WSGI server
- **Features**: OCR, ML, Blockchain, WebGIS
- **Health Check**: `/api/health`

### **Database Service (PostgreSQL)**
- **Port**: 5432
- **Version**: PostgreSQL 15
- **Features**: Persistent storage, Health checks
- **Data**: Stored in `postgres_data` volume

### **Cache Service (Redis)**
- **Port**: 6379
- **Version**: Redis 7
- **Features**: Session storage, Caching
- **Data**: Stored in `redis_data` volume

### **Frontend Service (Optional)**
- **Port**: 80
- **Framework**: React with Nginx
- **Features**: Static file serving, SPA routing

## 🔧 Configuration Files

### **Environment Variables (.env)**
```bash
# Database
POSTGRES_DB=fra_atlas
POSTGRES_USER=fra_user
POSTGRES_PASSWORD=your_secure_password

# Application
SECRET_KEY=your_secret_key
FLASK_ENV=production

# Ports
BACKEND_PORT=5000
FRONTEND_PORT=80
```

### **Docker Compose Features**
- ✅ **Multi-stage builds** for optimized images
- ✅ **Health checks** for all services
- ✅ **Persistent volumes** for data
- ✅ **Automatic restarts** on failure
- ✅ **Environment variable** configuration
- ✅ **Network isolation** with bridge network
- ✅ **Production-ready** Gunicorn configuration

## 🌐 Deployment Platforms

### **Railway.app Deployment**
1. Connect your GitHub repository
2. Railway will automatically detect Docker configuration
3. Set environment variables in Railway dashboard
4. Deploy with one click

### **AWS Lightsail Deployment**
1. Create Lightsail instance (Ubuntu 20.04)
2. Install Docker and Docker Compose
3. Clone repository and configure environment
4. Run `docker-compose -f docker-compose.production.yml up -d`

### **AWS EC2 Deployment**
1. Launch EC2 instance (t3.medium or larger)
2. Install Docker and Docker Compose
3. Configure security groups (ports 80, 5000, 5432)
4. Deploy using docker-compose

## 🔍 Monitoring & Maintenance

### **Health Checks**
```bash
# Check all services
docker-compose -f docker-compose.production.yml ps

# Check specific service logs
docker-compose -f docker-compose.production.yml logs backend
docker-compose -f docker-compose.production.yml logs db
```

### **Backup Database**
```bash
# Create backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U fra_user fra_atlas > backup.sql

# Restore backup
docker-compose -f docker-compose.production.yml exec -T db psql -U fra_user fra_atlas < backup.sql
```

### **Update Application**
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build
```

## 🛡️ Security Features

- **Non-root users** in containers
- **Security headers** in Nginx
- **Environment variable** secrets
- **Network isolation** between services
- **Health checks** for service monitoring
- **Resource limits** and restart policies

## 📊 Performance Optimizations

- **Multi-stage builds** for smaller images
- **Gzip compression** for web content
- **Connection pooling** for database
- **Redis caching** for sessions
- **Static file serving** via Nginx
- **Worker processes** for Flask

## 🚨 Troubleshooting

### **Common Issues**
1. **Port conflicts**: Check if ports 80, 5000, 5432 are available
2. **Permission issues**: Ensure Docker has proper permissions
3. **Database connection**: Verify environment variables
4. **Memory issues**: Increase Docker memory limits

### **Debug Commands**
```bash
# Check container logs
docker-compose -f docker-compose.production.yml logs -f backend

# Access container shell
docker-compose -f docker-compose.production.yml exec backend bash

# Check database connection
docker-compose -f docker-compose.production.yml exec backend python -c "import psycopg2; print('DB OK')"
```

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] Database passwords secured
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Domain name configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Security headers enabled
- [ ] Performance testing completed

**Your FRA-SENTINEL application is now ready for production deployment!** 🎉


