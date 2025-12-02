"""
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from container import create_container
from infrastructure.api.appointment import router as appointment_router
from infrastructure.api.patient import router as patient_router
from infrastructure.api.provider import router as provider_router
from infrastructure.api.user import router as user_router
from services.errors import ServiceError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """
    # Startup: container is already set up by setup_dishka
    yield
    # Shutdown: close the container to release resources
    await app.state.dishka_container.close()


app = FastAPI(
    title="Patient Triage & Management System",
    description="API for patient triage, provider management, and appointment scheduling",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup Dishka dependency injection
container = create_container()
setup_dishka(container, app)

@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """
    Global handler for all ServiceError exceptions.
    
    Converts domain errors to HTTP responses automatically.
    No try-except needed in route handlers.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api/v1")
app.include_router(provider_router, prefix="/api/v1")
app.include_router(appointment_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Patient Triage & Management System API"}

