# How to Host FRA-SENTINEL on Firebase and Vercel

This guide provides step-by-step instructions for deploying the FRA-SENTINEL application (a Flask-based web app with PostgreSQL database and Redis cache) to Firebase Cloud Run and Vercel using Docker containers.

## Prerequisites

- Docker and Docker Compose installed
- Git repository with the FRA-SENTINEL code
- Firebase CLI (for Firebase deployment)
- Vercel CLI (for Vercel deployment)
- Google Cloud account (for Firebase)
- Vercel account

## Project Overview

FRA-SENTINEL is a containerized Flask application that includes:
- **Backend**: Flask web server with OCR, ML, and WebGIS features
- **Database**: PostgreSQL for data storage
- **Cache**: Redis for session and data caching

The application uses Docker Compose for local development and can be deployed as containers to cloud platforms.

## Deployment to Firebase (Cloud Run)

Firebase Cloud Run allows you to run containerized applications in a serverless environment.

### Step 1: Set up Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Cloud Run in the project

### Step 2: Install Firebase CLI

```bash
npm install -g firebase-tools
firebase login
```

### Step 3: Prepare the Application

1. Clone the repository:
```bash
git clone <your-repo-url>
cd FRA-SENTINEL
```

2. Create environment variables file (`.env`):
```bash
POSTGRES_DB=fra_atlas
POSTGRES_USER=fra_user
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=redis_password_2025
SECRET_KEY=your_secret_key
```

3. Build the Docker image:
```bash
docker build -f Dockerfile.backend -t fra-sentinel-backend .
```

### Step 4: Deploy to Cloud Run

1. Initialize Firebase in your project:
```bash
firebase init
# Select "Cloud Run" when prompted
```

2. Deploy the container:
```bash
firebase deploy --only hosting,functions
# For Cloud Run, use:
gcloud run deploy fra-sentinel \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars POSTGRES_DB=fra_atlas,POSTGRES_USER=fra_user,etc.
```

Note: For a full deployment with database, you may need to:
- Use Cloud SQL for PostgreSQL
- Use Memorystore for Redis
- Update the environment variables accordingly

### Step 5: Access the Application

After deployment, Firebase will provide a URL to access your application.

## Deployment to Vercel

Vercel supports Docker deployments, but this full-stack application with database and cache is **not recommended** for Vercel. Here's why and alternatives:

### Limitations for FRA-SENTINEL on Vercel:
- ❌ **No built-in database**: PostgreSQL and Redis would need external services
- ❌ **Serverless constraints**: ML/OCR processing may exceed execution time limits
- ❌ **File storage**: No persistent file storage for uploads
- ❌ **Cost**: Complex setup with multiple external services

### Possible Vercel Approach (Not Recommended):
1. Deploy Flask app as serverless functions
2. Use external PostgreSQL (Railway, PlanetScale)
3. Use external Redis (Upstash, Redis Labs)
4. Handle file uploads separately

**This would be complex and expensive. Better alternatives below.**

## Recommended Hosting Platforms

### 🥇 **Railway.app** (BEST CHOICE)
Railway is specifically designed for Docker applications like FRA-SENTINEL.

**Why Railway?**
- ✅ **One-click Docker deployment**
- ✅ **Built-in PostgreSQL and Redis**
- ✅ **Automatic scaling**
- ✅ **Free tier for small projects**
- ✅ **Perfect for full-stack apps**

**Railway Deployment Steps:**
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects `docker-compose.yml`
4. Set environment variables:
   ```
   POSTGRES_DB=fra_atlas
   POSTGRES_USER=fra_user
   POSTGRES_PASSWORD=your_secure_password
   REDIS_PASSWORD=redis_password
   SECRET_KEY=your_secret_key
   ```
5. Deploy automatically!

### 🥈 **Render** (Good Alternative)
Similar to Railway, supports Docker and databases.

### 🥉 **AWS/Google Cloud with Cloud Run**
More powerful but requires more setup.

## Quick Comparison

| Platform | Docker Support | Database | Ease of Use | Cost |
|----------|---------------|----------|-------------|------|
| Railway.app | ✅ Excellent | ✅ Built-in | ⭐⭐⭐⭐⭐ | Free tier |
| Vercel | ⚠️ Limited | ❌ External only | ⭐⭐⭐ | Paid |
| Render | ✅ Good | ✅ Built-in | ⭐⭐⭐⭐ | Free tier |
| AWS | ✅ Excellent | ✅ Full control | ⭐⭐ | Variable |

## Final Recommendation

**Use Railway.app** for the easiest and most reliable deployment of FRA-SENTINEL. It's designed exactly for applications like yours with Docker, databases, and complex backends.

## Hybrid Approach: Vercel + Supabase

**Yes, Vercel + Supabase is technically possible** but requires significant modifications to the FRA-SENTINEL codebase. Here's the feasibility analysis:

### ✅ **What Works with Vercel + Supabase:**

1. **Database**: Supabase provides PostgreSQL (with PostGIS extension available)
2. **Authentication**: Supabase Auth for user management
3. **Real-time Features**: Supabase real-time subscriptions
4. **API Routes**: Can be converted to Vercel serverless functions
5. **Static Assets**: Frontend templates can be served statically

### ⚠️ **Major Challenges & Required Changes:**

1. **Flask App → Serverless Functions**: 
   - Convert each `@app.route` to individual Vercel API functions
   - Handle sessions differently (serverless functions are stateless)
   - Restructure the entire application architecture

2. **Redis Replacement**:
   - Supabase doesn't provide Redis
   - Need external Redis service (Upstash, Redis Labs)
   - Or use Supabase's built-in caching

3. **File Uploads & Processing**:
   - Vercel has limits on file processing
   - ML/OCR operations may exceed execution time limits
   - Need external storage (Supabase Storage, AWS S3, Cloudinary)

4. **Long-Running Tasks**:
   - OCR processing (3.2s) might work
   - Complex ML tasks may timeout

### 🔧 **Implementation Steps (Advanced):**

#### 1. **Set up Supabase**
```bash
# Install Supabase CLI
npm install -g supabase

# Initialize project
supabase init
supabase start

# Enable PostGIS
supabase db reset  # Then run migration with PostGIS
```

#### 2. **Modify Database Connection**
Update `webgis/database/__init__.py`:
```python
# Use Supabase connection string
DATABASE_URL = os.getenv('SUPABASE_DB_URL')
```

#### 3. **Convert Flask Routes to Vercel Functions**
Create `api/` directory with functions like:
```
api/
├── index.py          # Main dashboard
├── upload.py         # File upload handler
├── fra-data.py       # API endpoints
└── ...
```

#### 4. **Vercel Configuration**
`vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index"
    }
  ]
}
```

#### 5. **Environment Variables**
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_DB_URL=postgresql://...
REDIS_URL=your_redis_url  # External Redis
```

### 💰 **Cost Comparison:**

| Service | Cost | Notes |
|---------|------|-------|
| Vercel | $0-20/month | Serverless functions |
| Supabase | $0-25/month | Database + Auth |
| External Redis | $0-10/month | Upstash/Redis Labs |
| **Total** | **$0-55/month** | vs Railway's $0-10/month |

### 🎯 **Recommendation:**

**For FRA-SENTINEL, this hybrid approach is overkill.** The application is designed as a monolithic Flask app with Docker, making Railway.app a much better fit.

**Only pursue Vercel + Supabase if:**
- You want to learn serverless architecture
- You need Supabase's real-time features
- You're willing to refactor the entire codebase
- Cost is not a primary concern

**Stick with Railway.app** for the simplest, most reliable deployment! 🚀

## Environment Variables

Both platforms require the following environment variables:

- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `REDIS_PASSWORD`: Redis password
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Full database connection URL (for external DBs)

## Troubleshooting

### Common Issues

1. **Port Configuration**: Ensure your app listens on the port provided by the platform (e.g., `$PORT` for Cloud Run)
2. **Database Connection**: For Vercel, use external database services
3. **Memory Limits**: Monitor resource usage and adjust as needed
4. **Build Failures**: Check Docker build logs and ensure all dependencies are included

### Logs

- **Firebase**: Use `firebase functions:log` or Cloud Run logs in GCP Console
- **Vercel**: Check logs in the Vercel dashboard or use `vercel logs`

## Security Considerations

- Use strong, unique passwords for database and Redis
- Enable HTTPS (both platforms provide this by default)
- Regularly update dependencies and monitor for vulnerabilities
- Use environment variables for sensitive data

## Cost Considerations

- **Firebase Cloud Run**: Pay-per-use pricing based on CPU, memory, and requests
- **Vercel**: Generous free tier, paid plans for higher usage

For production deployments, consider using managed database services compatible with both platforms.