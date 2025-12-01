"""
Health Check Endpoints

Provides health check endpoints for the API.
"""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns the current health status of the API.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "patient-triage-api",
        "version": "0.1.0",
    }


@router.get("/health/ready")
async def readiness_check() -> dict[str, Any]:
    """
    Readiness check endpoint.
    
    Checks if the service is ready to accept traffic.
    This will include database connectivity checks in Phase 1.
    """
    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": "pending",  # Will be implemented in Phase 1
            "external_services": "pending",  # Will be implemented later
        },
    }


@router.get("/health/live")
async def liveness_check() -> dict[str, Any]:
    """
    Liveness check endpoint.
    
    Simple check to verify the service is alive.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
