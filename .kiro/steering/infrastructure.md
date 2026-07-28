---
inclusion: fileMatch
fileMatchPattern: "**/docker/**,**/docker-compose*,**/.env*,**/scripts/**"
---

# Infrastructure & Deployment Guidelines

## Docker Compose Architecture

### Service Definitions
All services are defined in `docker-compose.yml` at the project root. Services communicate via a shared Docker network (`qa-agent-net`).

### Container Naming Convention
- `qa-agent-app` — FastAPI core engine + LangGraph agent
- `qa-agent-playwright` — Playwright test runner (browsers pre-installed)
- `qa-agent-allure` — Allure Report Server
- `plane-web` — Plane.so frontend
- `plane-api` — Plane.so API backend
- `plane-db` — PostgreSQL for Plane.so
- `plane-redis` — Redis for Plane.so queue/cache

### Volume Mounts
```yaml
volumes:
  chroma-data:        # ChromaDB persistent vectors → ./data/chroma
  allure-results:     # Test results shared between runner and server
  plane-db-data:      # PostgreSQL data persistence
  story-data:         # User story documents input
```

### Network Configuration
```yaml
networks:
  qa-agent-net:
    driver: bridge
```
All services attach to `qa-agent-net` for internal DNS resolution.

## Dockerfile Standards

### Base Images
- Application: `python:3.11-slim`
- Playwright: `mcr.microsoft.com/playwright/python:v1.40.0-jammy`
- Allure: `frankescobar/allure-docker-service:latest`

### Multi-stage Builds
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ ./src/
```

### Health Checks
Every service must include a Docker health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## Environment Variables

### Required Variables (`.env`)
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
GEMINI_API_KEY=                    # Required for cloud fallback
GEMINI_MODEL=gemini-2.5-flash

# Plane.so Configuration
PLANE_API_URL=http://plane-api:8000
PLANE_API_KEY=                     # Generated from Plane.so admin
PLANE_WORKSPACE_SLUG=qa-workspace
PLANE_PROJECT_ID=

# FastAPI Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_ENV=development                # development | production
LOG_LEVEL=INFO

# ChromaDB
CHROMA_PERSIST_PATH=./data/chroma
CHROMA_COLLECTION=user_stories_v1

# Allure
ALLURE_RESULTS_PATH=./data/allure-results
ALLURE_SERVER_URL=http://qa-agent-allure:5050

# Crawler
CRAWL_MAX_DEPTH=3
CRAWL_MAX_PAGES=50
CRAWL_TIMEOUT_MS=10000
```

### Security Rules
- NEVER commit `.env` files to version control
- Use `.env.example` as template with empty sensitive values
- In production, inject secrets via Docker Secrets or environment override
- API keys must be rotated every 90 days

## Plane.so Setup

### Initial Configuration (via `scripts/setup_plane.sh`)
1. Create workspace with slug `qa-workspace`
2. Create project "QA Automation"
3. Configure board states: `TODO`, `DOING`, `FINISHED`, `FAILED`
4. Generate API key for service account
5. Register webhook pointing to `http://qa-agent-app:8000/webhooks/plane`

### Webhook Configuration
- Event type: Issue state change
- Filter: Transition to state `DOING`
- Target: `POST http://qa-agent-app:8000/webhooks/plane`
- Secret: Shared secret for signature validation

## Allure Server Setup

### Configuration
```yaml
allure:
  image: frankescobar/allure-docker-service
  ports:
    - "5050:5050"
  volumes:
    - allure-results:/app/allure-results
  environment:
    CHECK_RESULTS_EVERY_SECONDS: 5
    KEEP_HISTORY: 25
```

### Report Access
- Dashboard URL: `http://localhost:5050/allure-docker-service/latest-report`
- API for programmatic access: `http://localhost:5050/allure-docker-service/report/generate`

## Deployment Commands

### Development
```bash
# Start all services
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build app

# View logs
docker-compose logs -f app

# Run tests manually
docker-compose exec app pytest -m smoke --alluredir=/app/data/allure-results
```

### Production Considerations
- Use `docker-compose.prod.yml` override for production settings
- Enable resource limits (CPU, memory) per container
- Configure log rotation
- Use external PostgreSQL for Plane.so (not containerized)
- Set `APP_ENV=production` to disable debug endpoints
- Enable HTTPS via reverse proxy (nginx/caddy) in front of services

## Monitoring

- FastAPI `/health` endpoint returns service status and dependency checks
- Docker healthchecks auto-restart unhealthy containers
- Log aggregation via Docker logging driver (json-file with rotation)
- Allure server provides historical test trend data
