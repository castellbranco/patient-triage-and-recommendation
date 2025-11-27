"""
Patient Triage & Management System - Main FastAPI Application

This is the entry point for the backend API following Clean Architecture principles.
"""
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from presentation.api.public.v1 import health as public_health
# from presentation.api.internal import auth as internal_auth  # Uncomment in Phase 1


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager for startup and shutdown events.

    This will be used to:
    - Initialize database connections
    - Set up dependency injection container (Dishka)
    - Close connections on shutdown
    """
    # Startup
    print("🚀 Starting Patient Triage & Management System")
    print("📊 Database connection: Pending Phase 1 implementation")

    yield

    # Shutdown
    print("🛑 Shutting down Patient Triage & Management System")


# Create FastAPI application
app = FastAPI(
    title="Patient Triage & Management System API",
    description="Healthcare backend with symptom standardization via NLM Medical Conditions API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
# Read from environment in production
cors_origins = json.loads(
    """["http://localhost:3000","http://localhost:8501"]"""
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Public API routes (versioned)
app.include_router(
    public_health.router,
    prefix="/api/public/v1",
    tags=["Health Check"]
)

# Internal API routes (not versioned) - Uncomment in Phase 1
# app.include_router(
#     internal_auth.router,
#     prefix="/api/internal",
#     tags=["Authentication"]
# )


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information"""
    return {
        "message": "Patient Triage & Management System API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/public/v1/health",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    In production, this should log to monitoring service.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error",
        },
    )
