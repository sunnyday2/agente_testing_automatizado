# Main application container
# FastAPI core engine + LangGraph agent + RAG system + Playwright
#
# Build: docker build -f docker/Dockerfile -t qa-agent-app .
# Run:   docker run -p 8000:8000 --env-file .env qa-agent-app

FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ src/
COPY pyproject.toml .
COPY pytest.ini .

# Create data directories
RUN mkdir -p data/stories data/chroma data/allure-results

# Copy sample data
COPY data/stories/ data/stories/

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
