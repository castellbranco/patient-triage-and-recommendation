"""
Unit Tests for the Patient model.
"""

import pytest
from datetime import date
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from infrastructure.database.models.patient import Patient


@pytest.fixture
async def user_with_patient(db_session, user_factory, patient_factory):
    """Helper fixture to create user + patient."""

    async def _create(email, **patient_kwargs):
        user = user_factory(email=email, role="patient")
        db_session.add(user)
        await db_session.commit()
        patient = patient_factory(user_id=user.id, **patient_kwargs)
        db_session.add(patient)
        await db_session.commit()
        await db_session.refresh(patient)
        return patient

    return _create


@pytest.mark.asyncio
async def test_create_patient_success(user_with_patient):
    """Test successful creation of a Patient."""
    patient = await user_with_patient("patient@example.com", gender="male")

    assert patient.id is not None
    assert patient.gender == "male"


@pytest.mark.asyncio
async def test_read_patient_by_user_id(db_session, user_with_patient):
    """Test querying a patient by user_id."""
    patient = await user_with_patient("query@example.com")

    result = await db_session.execute(select(Patient).where(Patient.user_id == patient.user_id))
    assert result.scalar_one_or_none().id == patient.id


@pytest.mark.asyncio
async def test_patient_with_blood_type(user_with_patient):
    """Test patient with blood type."""
    patient = await user_with_patient("blood@example.com", blood_type="AB+")
    assert patient.blood_type == "AB+"


@pytest.mark.asyncio
async def test_patient_with_address(user_with_patient):
    """Test patient with address."""
    patient = await user_with_patient("addr@example.com", address_line1="123 Main St", city="NYC")

    assert patient.address_line1 == "123 Main St"
    assert patient.city == "NYC"


@pytest.mark.asyncio
async def test_patient_with_allergies(user_with_patient):
    """Test patient with allergies."""
    allergies = [{"name": "penicillin", "severity": "high"}]
    patient = await user_with_patient("allergy@example.com", allergies=allergies)
    assert patient.allergies == allergies


@pytest.mark.asyncio
async def test_patient_with_chronic_conditions(user_with_patient):
    """Test patient with chronic conditions."""
    conditions = [{"icd10": "E11", "name": "Type 2 diabetes"}]
    patient = await user_with_patient("chronic@example.com", chronic_conditions=conditions)
    assert patient.chronic_conditions == conditions


@pytest.mark.asyncio
async def test_patient_with_medications(user_with_patient):
    """Test patient with medications."""
    meds = [{"name": "metformin", "dosage": "500mg"}]
    patient = await user_with_patient("meds@example.com", medications=meds)
    assert patient.medications == meds


@pytest.mark.asyncio
async def test_patient_with_emergency_contact(user_with_patient):
    """Test patient with emergency contact."""
    contact = {"name": "John Doe", "phone": "+1234567890"}
    patient = await user_with_patient("emergency@example.com", emergency_contact=contact)
    assert patient.emergency_contact == contact


@pytest.mark.asyncio
async def test_patient_unique_user_id_constraint(db_session, user_factory, patient_factory):
    """Test duplicate user_id is rejected."""
    user = user_factory(email="unique@example.com", role="patient")
    db_session.add(user)
    await db_session.commit()

    db_session.add(patient_factory(user_id=user.id))
    await db_session.commit()

    db_session.add(patient_factory(user_id=user.id))
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_update_patient(db_session, user_with_patient):
    """Test updating patient fields."""
    patient = await user_with_patient("update@example.com", city="Old City")

    patient.city = "New City"
    patient.allergies = [{"name": "peanuts", "severity": "severe"}]
    await db_session.commit()
    await db_session.refresh(patient)

    assert patient.city == "New City"
    assert patient.allergies[0]["name"] == "peanuts"


@pytest.mark.asyncio
async def test_patient_user_relationship(user_with_patient):
    """Test patient-user relationship."""
    patient = await user_with_patient("relation@example.com")
    assert patient.user.email == "relation@example.com"


@pytest.mark.asyncio
async def test_patient_repr(user_with_patient):
    """Test string representation."""
    patient = await user_with_patient("repr@example.com", date_of_birth=date(1985, 3, 20))
    assert "1985-03-20" in repr(patient)


@pytest.mark.asyncio
async def test_filter_patients_by_gender(db_session, user_with_patient):
    """Test filtering by gender."""
    await user_with_patient("m@example.com", gender="male")
    await user_with_patient("f@example.com", gender="female")

    result = await db_session.execute(select(Patient).where(Patient.gender == "male"))
    assert len(result.scalars().all()) == 1
