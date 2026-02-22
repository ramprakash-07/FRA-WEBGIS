# AWS EC2/Lightsail Deployment Guide for FRA-SENTINEL
# Complete setup for Ubuntu server with Docker and production configuration

## 🚀 Prerequisites

- **AWS Account** with EC2 or Lightsail access
- **Domain name** (optional, for custom domain)
- **SSH client** (PuTTY on Windows, Terminal on Mac/Linux)
- **Basic knowledge** of Linux commands

## 📋 Step 1: Launch EC2/Lightsail Instance

### **EC2 Instance Setup**

1. **Launch EC2 Instance**:
   - **AMI**: Ubuntu Server 20.04 LTS or 22.04 LTS
   - **Instance Type**: t3.medium (2 vCPU, 4GB RAM) minimum
   - **Storage**: 20GB SSD minimum
   - **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Configure Security Group**:
   ```
   Type           Protocol    Port Range    Source
   SSH            TCP         22            Your IP
   HTTP           TCP         80            0.0.0.0/0
   HTTPS          TCP         443           0.0.0.0/0
   Custom TCP     TCP         5000          0.0.0.0/0 (for direct backend access)
   ```

### **Lightsail Instance Setup**

1. **Create Lightsail Instance**:
   - **Platform**: Linux/Unix
   - **Blueprint**: Ubuntu 20.04 LTS
   - **Instance Plan**: $10/month (1GB RAM, 1 vCPU) minimum
   - **Add storage**: 20GB SSD

2. **Configure Firewall**:
   ```
   Application     Protocol    Port Range
   SSH            TCP         22
   HTTP           TCP         80
   HTTPS          TCP         443
   Custom         TCP         5000
   ```

## 🔧 Step 2: Server Setup and Configuration

### **Connect to Your Instance**

```bash
# Replace with your instance IP
ssh -i your-key.pem ubuntu@your-instance-ip
```

### **Update System Packages**

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop unzip software-properties-common
```

### **Install Docker**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### **Configure Firewall (UFW)**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow direct backend access (optional)
sudo ufw allow 5000

# Check status
sudo ufw status
```

## 📁 Step 3: Deploy Application

### **Clone Repository**

```bash
# Clone your repository
git clone https://github.com/your-username/fra-sentinel.git
cd fra-sentinel

# Or upload your code via SCP
# scp -i your-key.pem -r ./fra-sentinel ubuntu@your-instance-ip:~/
```

### **Configure Environment Variables**

```bash
# Copy production environment template
cp docker/env.prod.example .env.prod

# Edit environment variables
nano .env.prod
```

**Required Environment Variables**:
```bash
# Database Configuration
POSTGRES_DB=fra_atlas_prod
POSTGRES_USER=fra_user
POSTGRES_PASSWORD=your-secure-database-password

# Redis Configuration
REDIS_PASSWORD=your-secure-redis-password

# Application Configuration
SECRET_KEY=your-super-secure-secret-key
FLASK_ENV=production
DEBUG=False

# Production URLs
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://your-domain.com/api

# Service Ports
NGINX_PORT=80
NGINX_SSL_PORT=443
```

### **Deploy with Docker Compose**

```bash
# Start production services
docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d

# Check service status
docker-compose -f docker/docker-compose.prod.yml ps

# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

## 🌐 Step 4: Domain and SSL Configuration

### **Configure Domain (Optional)**

1. **Point your domain** to your server IP:
   - **A Record**: `@` → `your-server-ip`
   - **CNAME**: `www` → `your-domain.com`

2. **Update environment variables**:
   ```bash
   FRONTEND_URL=https://your-domain.com
   BACKEND_URL=https://your-domain.com/api
   ```

### **Install SSL Certificate with Certbot**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Configure Nginx for SSL
sudo nano /etc/nginx/sites-available/fra-sentinel
```

**Nginx SSL Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Docker containers
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fra-sentinel /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Step 5: Monitoring and Maintenance

### **Set Up Log Rotation**

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/fra-sentinel
```

```bash
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### **Set Up Health Monitoring**

```bash
# Create health check script
sudo nano /usr/local/bin/fra-sentinel-health.sh
```

```bash
#!/bin/bash
# Health check script for FRA-SENTINEL

# Check if services are running
if ! docker-compose -f /home/ubuntu/fra-sentinel/docker/docker-compose.prod.yml ps | grep -q "Up"; then
    echo "FRA-SENTINEL services are down!"
    # Restart services
    cd /home/ubuntu/fra-sentinel
    docker-compose -f docker/docker-compose.prod.yml up -d
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "Disk space is low: $DISK_USAGE%"
fi
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/fra-sentinel-health.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /usr/local/bin/fra-sentinel-health.sh
```

### **Set Up Backups**

```bash
# Create backup script
sudo nano /usr/local/bin/fra-sentinel-backup.sh
```

```bash
#!/bin/bash
# Backup script for FRA-SENTINEL

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f /home/ubuntu/fra-sentinel/docker/docker-compose.prod.yml exec -T db pg_dump -U fra_user fra_atlas_prod > $BACKUP_DIR/database_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz /home/ubuntu/fra-sentinel/data

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/fra-sentinel-backup.sh

# Add to crontab (daily backup at 2 AM)
crontab -e
# Add: 0 2 * * * /usr/local/bin/fra-sentinel-backup.sh
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Docker Permission Denied**:
   ```bash
   # Logout and login again to apply docker group changes
   exit
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

2. **Port Already in Use**:
   ```bash
   # Check what's using the port
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   
   # Stop conflicting services
   sudo systemctl stop apache2
   sudo systemctl disable apache2
   ```

3. **SSL Certificate Issues**:
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificate manually
   sudo certbot renew --dry-run
   ```

4. **Database Connection Issues**:
   ```bash
   # Check database logs
   docker-compose -f docker/docker-compose.prod.yml logs db
   
   # Test database connection
   docker-compose -f docker/docker-compose.prod.yml exec db psql -U fra_user -d fra_atlas_prod -c "SELECT version();"
   ```

### **Useful Commands**

```bash
# View all running containers
docker ps

# View container logs
docker-compose -f docker/docker-compose.prod.yml logs -f backend

# Restart specific service
docker-compose -f docker/docker-compose.prod.yml restart backend

# Update application
git pull origin main
docker-compose -f docker/docker-compose.prod.yml up -d --build

# Check system resources
htop
df -h
free -h
```

## 📊 Performance Optimization

### **System Optimization**

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### **Docker Optimization**

```bash
# Clean up unused Docker resources
docker system prune -a

# Monitor Docker resource usage
docker stats
```

## ✅ Deployment Checklist

- [ ] EC2/Lightsail instance launched
- [ ] Security groups/firewall configured
- [ ] Docker and Docker Compose installed
- [ ] Application code deployed
- [ ] Environment variables configured
- [ ] Services running with docker-compose
- [ ] Domain configured (if using custom domain)
- [ ] SSL certificate installed
- [ ] Health monitoring setup
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Performance testing completed

## 🎉 Success!

Your FRA-SENTINEL application is now deployed on AWS with:

- ✅ **Production-ready** Docker containers
- ✅ **PostgreSQL database** with PostGIS
- ✅ **Redis caching** for sessions
- ✅ **SSL encryption** with Let's Encrypt
- ✅ **Health monitoring** and logging
- ✅ **Automated backups**
- ✅ **Firewall protection**

**Your application is live and ready for production use!**


