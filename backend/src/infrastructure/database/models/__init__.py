"""
Database Models Package

Imports all models so Alembic can detect them for autogenerate.
"""

from infrastructure.database.models.user import User
from infrastructure.database.models.patient import Patient
from infrastructure.database.models.provider import Provider
from infrastructure.database.models.appointment import Appointment

__all__ = [
    "User",
    "Patient",
    "Provider",
    "Appointment",
]
