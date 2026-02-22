# Railway.app Deployment Guide for FRA-SENTINEL
# Step-by-step deployment instructions for Railway.app

## 🚀 Railway.app Deployment Steps

### **Step 1: Connect GitHub Repository**

1. **Sign up/Login** to [Railway.app](https://railway.app)
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your FRA-SENTINEL repository**
4. **Choose the main branch** (usually `main` or `master`)

### **Step 2: Configure Build Settings**

Railway will automatically detect your Docker configuration, but verify:

1. **Build Command**: `docker build -f docker/Dockerfile.backend -t fra-sentinel .`
2. **Start Command**: `gunicorn --config gunicorn.conf.py webgis.app:app`
3. **Port**: `5000` (Railway will automatically assign `$PORT`)

### **Step 3: Add Database Service**

1. **Click "New"** → **"Database"** → **"PostgreSQL"**
2. **Wait for provisioning** (usually 1-2 minutes)
3. **Note the connection details**:
   - `DATABASE_URL` (automatically provided)
   - `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

### **Step 4: Add Redis Service**

1. **Click "New"** → **"Database"** → **"Redis"**
2. **Wait for provisioning** (usually 1-2 minutes)
3. **Note the connection details**:
   - `REDIS_URL` (automatically provided)
   - `REDISHOST`, `REDISPORT`, `REDISPASSWORD`

### **Step 5: Configure Environment Variables**

Go to your main service → **"Variables"** tab and add:

```bash
# Application Configuration
SECRET_KEY=your-super-secure-secret-key-here
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=info

# External URLs (Railway will provide these)
FRONTEND_URL=https://your-app-name.up.railway.app
BACKEND_URL=https://your-app-name.up.railway.app

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
LOGGLY_TOKEN=your-loggly-token

# OCR Configuration
TESSERACT_CMD=/usr/bin/tesseract
GDAL_DATA=/usr/share/gdal
PROJ_LIB=/usr/share/proj
```

### **Step 6: Configure Health Checks**

1. **Go to your service** → **"Settings"** tab
2. **Set Health Check Path**: `/api/health`
3. **Set Health Check Timeout**: `30s`
4. **Enable Auto-Deploy**: Toggle on for automatic deployments

### **Step 7: Deploy and Test**

1. **Click "Deploy"** to trigger the first deployment
2. **Monitor the build logs** for any errors
3. **Wait for deployment** to complete (usually 3-5 minutes)
4. **Test your application** at the provided Railway URL

## 🔧 Railway-Specific Configuration

### **Railway.toml Configuration**

Create `railway.toml` in your project root:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "docker/Dockerfile.backend"

[deploy]
startCommand = "gunicorn --config gunicorn.conf.py webgis.app:app"
healthcheckPath = "/api/health"
healthcheckTimeout = 30
restartPolicyType = "always"

[environments.production]
variables = { FLASK_ENV = "production", DEBUG = "False" }
```

### **Environment Variable Priority**

Railway automatically provides these variables (don't override them):

- `RAILWAY_STATIC_URL`
- `RAILWAY_PUBLIC_DOMAIN`
- `RAILWAY_ENVIRONMENT`
- `PORT` (use this instead of hardcoded 5000)
- `DATABASE_URL` (if using Railway Postgres)
- `REDIS_URL` (if using Railway Redis)

## 🛡️ Security Considerations

### **Secrets Management**

1. **Never commit secrets** to your repository
2. **Use Railway's Variables** for sensitive data
3. **Enable Railway's built-in security** features
4. **Set up proper CORS** in your Flask app

### **Database Security**

1. **Use Railway's managed Postgres** (automatically secured)
2. **Enable connection pooling** in your app
3. **Use SSL connections** (Railway provides this automatically)

## 📊 Monitoring and Logs

### **Viewing Logs**

1. **Go to your service** → **"Deployments"** tab
2. **Click on a deployment** to view logs
3. **Use Railway CLI** for real-time logs:
   ```bash
   npm install -g @railway/cli
   railway login
   railway logs
   ```

### **Health Monitoring**

Railway automatically monitors:
- **Service health** via health check endpoint
- **Resource usage** (CPU, Memory)
- **Response times**
- **Error rates**

## 🚨 Troubleshooting

### **Common Issues**

1. **Build Failures**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Ensure proper file paths

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` is set correctly
   - Check if Postgres service is running
   - Ensure proper network connectivity

3. **Memory Issues**:
   - Railway has memory limits
   - Optimize your Docker image size
   - Use multi-stage builds

4. **Port Issues**:
   - Always use `$PORT` environment variable
   - Don't hardcode port numbers

### **Debug Commands**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Connect to your project
railway link

# View logs
railway logs

# Open shell in running container
railway shell

# Check service status
railway status
```

## 🔄 CI/CD Integration

### **Automatic Deployments**

Railway automatically deploys when you push to your connected branch:

1. **Push to main branch** → **Automatic deployment**
2. **Create pull request** → **Preview deployment**
3. **Merge pull request** → **Production deployment**

### **GitHub Actions Integration**

Create `.github/workflows/railway.yml`:

```yaml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railwayapp/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📈 Performance Optimization

### **Railway Limits**

- **Memory**: Up to 8GB (depending on plan)
- **CPU**: Shared resources
- **Storage**: Ephemeral (data not persisted)
- **Network**: Global CDN included

### **Optimization Tips**

1. **Use Railway's Postgres addon** for persistent data
2. **Implement proper caching** with Redis
3. **Optimize Docker images** with multi-stage builds
4. **Use connection pooling** for database connections
5. **Implement health checks** for better monitoring

## ✅ Deployment Checklist

- [ ] Repository connected to Railway
- [ ] PostgreSQL addon provisioned
- [ ] Redis addon provisioned
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] Domain configured (if using custom domain)
- [ ] SSL certificate active
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Performance testing completed

## 🎉 Success!

Your FRA-SENTINEL application is now deployed on Railway.app with:

- ✅ **Automatic deployments** on code push
- ✅ **Managed database** with PostGIS support
- ✅ **Redis caching** for sessions
- ✅ **Health monitoring** and logging
- ✅ **Global CDN** for fast access
- ✅ **SSL certificates** automatically managed

**Your application is live and ready for production use!**
