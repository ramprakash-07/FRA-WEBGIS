# Multi-stage Dockerfile for FRA-SENTINEL
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tam \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgdal-dev \
    gdal-bin \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_enhanced.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_enhanced.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models /app/uploads /app/temp

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Default command
CMD ["python", "webgis/app.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-mock \
    black \
    flake8 \
    isort \
    jupyter

# Override command for development
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

# Production stage
FROM base as production

# Install production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    gevent

# Copy production configuration
COPY docker/production.conf /app/

# Override command for production
CMD ["gunicorn", "--config", "production.conf", "webgis.app:app"]

# Worker stage for background tasks
FROM base as worker

# Install additional worker dependencies
RUN pip install --no-cache-dir \
    celery \
    redis

# Copy worker configuration
COPY docker/worker.conf /app/

# Override command for worker
CMD ["celery", "-A", "webgis.tasks", "worker", "--loglevel=info"]

# ML stage for model training
FROM base as ml

# Install ML dependencies
RUN pip install --no-cache-dir \
    mlflow \
    tensorflow \
    torch \
    torchvision \
    opencv-python \
    scikit-learn \
    pandas \
    numpy \
    matplotlib \
    seaborn

# Copy ML scripts
COPY ml/ /app/ml/

# Override command for ML training
CMD ["python", "ml/train_models.py"]









