"""Health check endpoint with dependency status.

Provides system health information including service connectivity
checks for ChromaDB, Ollama, Plane.so, and Allure.

Usage:
    GET /health — returns system health status and dependency checks
"""

from datetime import datetime, timezone

import httpx
from fastapi import APIRouter

from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """System health check with dependency status.

    Returns:
        JSON object with overall status, timestamp, version,
        and individual dependency health checks.
    """
    settings = get_settings()

    checks = {
        "chromadb": await _check_chromadb(settings),
        "ollama": await _check_ollama(settings),
        "plane": await _check_plane(settings),
    }

    # Overall status: healthy if all critical services are up
    critical_services = ["chromadb"]
    all_critical_healthy = all(
        checks.get(svc, {}).get("status") == "healthy"
        for svc in critical_services
    )

    overall_status = "healthy" if all_critical_healthy else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "environment": settings.environment,
        "checks": checks,
    }


async def _check_chromadb(settings) -> dict:
    """Check ChromaDB connectivity.

    Args:
        settings: Application settings.

    Returns:
        Health check result dict.
    """
    try:
        import chromadb

        client = chromadb.PersistentClient(path=settings.chromadb.persist_directory)
        # Attempt to list collections as a connectivity check
        collections = client.list_collections()
        return {
            "status": "healthy",
            "collections_count": len(collections),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def _check_ollama(settings) -> dict:
    """Check Ollama service connectivity.

    Args:
        settings: Application settings.

    Returns:
        Health check result dict.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return {
                    "status": "healthy",
                    "available_models": models[:5],
                }
            return {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
        }


async def _check_plane(settings) -> dict:
    """Check Plane.so API connectivity.

    Args:
        settings: Application settings.

    Returns:
        Health check result dict.
    """
    if not settings.plane.api_key:
        return {
            "status": "not_configured",
            "error": "PLANE_API_KEY not set",
        }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.plane.base_url}/api/v1/users/me/",
                headers={"X-API-Key": settings.plane.api_key},
            )
            if response.status_code == 200:
                return {"status": "healthy"}
            return {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
        }
