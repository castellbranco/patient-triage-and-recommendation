"""
Unit Tests for the Appointment model.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import select

from infrastructure.database.models.appointment import Appointment


@pytest.fixture
async def setup_patient_provider(db_session, user_factory, patient_factory, provider_factory):
    """Create a patient and provider for appointment tests."""
    u_p = user_factory(email="patient@example.com", role="patient")
    u_d = user_factory(email="provider@example.com", role="provider")
    db_session.add_all([u_p, u_d])
    await db_session.commit()
    
    patient = patient_factory(user_id=u_p.id)
    provider = provider_factory(user_id=u_d.id)
    db_session.add_all([patient, provider])
    await db_session.commit()
    return patient, provider


@pytest.fixture
async def create_appt(db_session, appointment_factory):
    """Helper to create appointments."""
    async def _create(patient_id, provider_id, **kwargs):
        kwargs.setdefault("appointment_datetime", datetime.now() + timedelta(days=1))
        appt = appointment_factory(patient_id=patient_id, provider_id=provider_id, **kwargs)
        db_session.add(appt)
        await db_session.commit()
        await db_session.refresh(appt)
        return appt
    return _create


@pytest.mark.asyncio
async def test_create_appointment_success(setup_patient_provider, create_appt):
    """Test successful creation of an Appointment."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id, duration=30)
    
    assert appt.id is not None
    assert appt.patient_id == patient.id
    assert appt.duration == 30


@pytest.mark.asyncio
async def test_appointment_default_status(setup_patient_provider, create_appt):
    """Test default status is 'scheduled'."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id)
    assert appt.status == "scheduled"


@pytest.mark.asyncio
async def test_appointment_with_chief_complaint(setup_patient_provider, create_appt):
    """Test appointment with chief complaint."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id, chief_complaint="Headache")
    assert appt.chief_complaint == "Headache"


@pytest.mark.asyncio
async def test_appointment_with_symptoms(setup_patient_provider, create_appt):
    """Test appointment with symptoms."""
    patient, provider = setup_patient_provider
    symptoms = [{"icd10": "R51", "name": "Headache"}]
    appt = await create_appt(patient.id, provider.id, symptoms=symptoms)
    assert appt.symptoms == symptoms


@pytest.mark.asyncio
async def test_appointment_with_diagnosis(setup_patient_provider, create_appt):
    """Test appointment with diagnosis."""
    patient, provider = setup_patient_provider
    diagnosis = [{"icd10": "J00", "name": "Common cold"}]
    appt = await create_appt(patient.id, provider.id, diagnosis=diagnosis)
    assert appt.diagnosis == diagnosis


@pytest.mark.asyncio
async def test_appointment_type(setup_patient_provider, create_appt):
    """Test appointment type."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id, type="telemedicine")
    assert appt.type == "telemedicine"


@pytest.mark.asyncio
async def test_appointment_notes(setup_patient_provider, create_appt):
    """Test appointment with notes."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id, notes="Morning preferred")
    assert appt.notes == "Morning preferred"


@pytest.mark.asyncio
async def test_update_appointment_status(db_session, setup_patient_provider, create_appt):
    """Test updating appointment status."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id)
    
    appt.status = "confirmed"
    await db_session.commit()
    await db_session.refresh(appt)
    assert appt.status == "confirmed"


@pytest.mark.asyncio
async def test_appointment_relationships(setup_patient_provider, create_appt):
    """Test appointment relationships."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id)
    
    assert appt.patient.id == patient.id
    assert appt.provider.id == provider.id


@pytest.mark.asyncio
async def test_appointment_repr(setup_patient_provider, create_appt):
    """Test string representation."""
    patient, provider = setup_patient_provider
    appt = await create_appt(patient.id, provider.id)
    assert "scheduled" in repr(appt)


@pytest.mark.asyncio
async def test_filter_appointments_by_status(db_session, setup_patient_provider, create_appt):
    """Test filtering by status."""
    patient, provider = setup_patient_provider
    
    t1, t2 = datetime.now() + timedelta(days=1), datetime.now() + timedelta(days=2)
    await create_appt(patient.id, provider.id, appointment_datetime=t1, status="scheduled")
    await create_appt(patient.id, provider.id, appointment_datetime=t2, status="confirmed")
    
    result = await db_session.execute(select(Appointment).where(Appointment.status == "scheduled"))
    assert len(result.scalars().all()) == 1
