"""
Pytest configuration and fixtures for testing.
"""

import asyncio, os, uuid, pytest, pytest_asyncio

from datetime import date, datetime, timedelta
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.infrastructure.database.base import Base, create_database_engine
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.patient import Patient
from app.infrastructure.database.models.appointment import Appointment
from app.infrastructure.database.models.provider import Provider

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/triage_test_db"
)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
 """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create a test database engine for the entire test session.
    """
    engine = create_database_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a test database session with automatic rollback.
    """
    async with test_engine.connect() as connection:
        await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession
        )

        async with session_factory() as session:
            yield session



@pytest.fixture
def user_factory():
    """
    Factory for creating test users with different roles.
    """
    def _create_user(
        role: str = "patient",
        email: str = None,
        is_active: bool = True,
        is_verified: bool = True,
        **kwargs
    ):
        if email is None:
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"

        user_data = {
            "email": email,
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lM7X8Gj0kGsW",  # "password123"
            "first_name": kwargs.get("first_name", "Test"),
            "last_name": kwargs.get("last_name", "User"),
            "phone_number": kwargs.get("phone_number", "+1234567890"),
            "role": role,
            "is_active": is_active,
            "is_verified": is_verified,
        }

        return User(**user_data)

    return _create_user


@pytest.fixture
def patient_factory():
    """
    Factory for creating test patients.
    """
    def _create_patient(
        user_id: uuid.UUID = None,
        date_of_birth: date = None,
        **kwargs
    ):
        if date_of_birth is None:
            date_of_birth = date(1990, 1, 1)

        patient_data = {
            "user_id": user_id,
            "date_of_birth": date_of_birth,
            "gender": kwargs.get("gender", "male"),
            "blood_type": kwargs.get("blood_type", "O+"),
            "address_line1": kwargs.get("address_line1", "123 Test St"),
            "city": kwargs.get("city", "Test City"),
            "allergies": kwargs.get("allergies", []),
            "chronic_conditions": kwargs.get("chronic_conditions", []),
            "medications": kwargs.get("medications", []),
            "emergency_contact": kwargs.get("emergency_contact", {}),
        }

        return Patient(**patient_data)

    return _create_patient


@pytest.fixture
def provider_factory():
    """Factory for creating test providers."""
    def _create_provider(
        user_id: uuid.UUID = None,
        specialty: str = "General Practice",
        license_number: str = None,
        **kwargs
    ):
        if license_number is None:
            license_number = f"LIC-{uuid.uuid4().hex[:8].upper()}"

        provider_data = {
            "user_id": user_id,
            "specialty": specialty,
            "license_number": license_number,
            "credentials": kwargs.get("credentials", "MD"),
            "languages_spoken": kwargs.get("languages_spoken", ["English"]),
            "accepted_insurances": kwargs.get("accepted_insurances", []),
            "certifications": kwargs.get("certifications", []),
            "accepting_new_patients": kwargs.get("accepting_new_patients", True),
            "years_of_experience": kwargs.get("years_of_experience", 5),
        }

        return Provider(**provider_data)

    return _create_provider


@pytest.fixture
def appointment_factory():
    """Factory for creating test appointments."""
    def _create_appointment(
        patient_id: uuid.UUID = None,
        provider_id: uuid.UUID = None,
        appointment_datetime: datetime = None,
        **kwargs
    ):
        if appointment_datetime is None:
            appointment_datetime = datetime.now() + timedelta(days=1)
            appointment_datetime = appointment_datetime.replace(hour=10, minute=0, second=0)

        appointment_data = {
            "patient_id": patient_id,
            "provider_id": provider_id,
            "appointment_datetime": appointment_datetime,
            "duration": kwargs.get("duration", 30),
            "status": kwargs.get("status", "scheduled"),
            "type": kwargs.get("type", "consultation"),
            "chief_complaint": kwargs.get("chief_complaint"),
            "symptoms": kwargs.get("symptoms", []),
            "diagnosis": kwargs.get("diagnosis", []),
            "notes": kwargs.get("notes"),
        }

        return Appointment(**appointment_data)

    return _create_appointment