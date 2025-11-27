"""
Database Models Package

Imports all models so Alembic can detect them for autogenerate.
"""
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.patient import Patient
from app.infrastructure.database.models.provider import Provider
from app.infrastructure.database.models.appointment import Appointment

__all__ = [
    "User",
    "Patient",
    "Provider",
    "Appointment",
]
