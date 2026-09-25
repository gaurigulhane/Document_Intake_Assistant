# ==========================================
# STAGE 1: Build React Frontend (Vite)
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ==========================================
# STAGE 2: Python FastAPI Backend + Static Files
# ==========================================
FROM python:3.11-slim AS production
WORKDIR /app

# Prevent Python writing pyc files to disc & buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app
COPY backend/tests ./tests

# Copy compiled React frontend static files from Stage 1
COPY --from=frontend-builder /frontend/dist ./static

# Expose FastAPI port
EXPOSE 8000

# Default environment variables
ENV APP_ENV=production
ENV LLM_PROVIDER=mock
ENV DATABASE_URL=sqlite:///./document_intake.db
ENV ALLOWED_ORIGINS=*

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
