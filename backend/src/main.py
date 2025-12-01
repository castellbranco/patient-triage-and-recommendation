"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.appointment import router as appointment_router
from infrastructure.api.patient import router as patient_router
from infrastructure.api.provider import router as provider_router
from infrastructure.api.user import router as user_router

app = FastAPI(
    title="Patient Triage & Management System",
    description="API for patient triage, provider management, and appointment scheduling",
    version="0.1.0",
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

