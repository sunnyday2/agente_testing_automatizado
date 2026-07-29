# Multi-stage Dockerfile for QA Automation Agent
# Stage 1: Build frontend (Node.js)
# Stage 2: Production app (Python + built frontend)
#
# Build: docker build -f docker/Dockerfile -t qa-agent-app .
# Run:   docker run -p 8000:8000 --env-file .env qa-agent-app

# ============================================================
# Stage 1: Frontend Build
# ============================================================
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Install dependencies first (better layer caching)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts && npm rebuild esbuild

# Copy frontend source and build
COPY frontend/ .
RUN npm run build || npx vite build

# ============================================================
# Stage 2: Python Production Image
# ============================================================
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy AS production

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Copy application source
COPY src/ src/
COPY scripts/ scripts/
COPY pyproject.toml .
COPY pytest.ini .

# Create data directories
RUN mkdir -p data/stories data/chroma data/allure-results

# Copy sample data
COPY data/stories/ data/stories/

# Set environment for production
ENV ENVIRONMENT=production

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start server
CMD ["sh", "-c", "python scripts/migrate.py && python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000"]
