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

Vercel supports Docker deployments and can run containerized applications.

### Step 1: Set up Vercel Account

1. Go to [Vercel](https://vercel.com/)
2. Sign up or log in
3. Install Vercel CLI:
```bash
npm install -g vercel
vercel login
```

### Step 2: Prepare the Application

1. Ensure your project has a `Dockerfile` (use `Dockerfile.backend` for the Flask app)
2. Create a `vercel.json` configuration file:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "Dockerfile.backend",
      "use": "@vercel/docker"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "POSTGRES_DB": "fra_atlas",
    "POSTGRES_USER": "fra_user",
    "POSTGRES_PASSWORD": "your_secure_password",
    "REDIS_PASSWORD": "redis_password_2025",
    "SECRET_KEY": "your_secret_key"
  }
}
```

### Step 3: Deploy to Vercel

1. Deploy using Vercel CLI:
```bash
vercel --prod
```

2. Or connect your GitHub repository in the Vercel dashboard for automatic deployments.

### Important Notes for Vercel Deployment

- **Database**: Vercel doesn't provide managed databases like PostgreSQL or Redis. You'll need to use external services (e.g., Railway, PlanetScale, or Upstash for Redis).
- **Environment Variables**: Set them in the Vercel dashboard or via CLI.
- **Scaling**: Vercel automatically scales your application, but for database-heavy apps, consider the limitations.

### Step 4: Access the Application

Vercel will provide a deployment URL (e.g., `https://fra-sentinel.vercel.app`).

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