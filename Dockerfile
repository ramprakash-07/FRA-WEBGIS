FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY FRASENTINEL/001/FRA-SENTINEL/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy only the deployable FRA-SENTINEL app.
COPY FRASENTINEL/001/FRA-SENTINEL /app

WORKDIR /app/webgis

# Railway injects PORT; wsgi.py already honors it.
CMD ["python", "wsgi.py"]
