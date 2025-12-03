"""
Unit Tests for the Provider model.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from infrastructure.database.models.provider import Provider


@pytest.fixture
async def user_with_provider(db_session, user_factory, provider_factory):
    """Helper fixture to create user + provider."""

    async def _create(email, **provider_kwargs):
        user = user_factory(email=email, role="provider")
        db_session.add(user)
        await db_session.commit()
        provider = provider_factory(user_id=user.id, **provider_kwargs)
        db_session.add(provider)
        await db_session.commit()
        await db_session.refresh(provider)
        return provider

    return _create


@pytest.mark.asyncio
async def test_create_provider_success(user_with_provider):
    """Test successful creation of a Provider."""
    provider = await user_with_provider(
        "prov@example.com", specialty="Cardiology", license_number="LIC-123"
    )

    assert provider.id is not None
    assert provider.specialty == "Cardiology"
    assert provider.license_number == "LIC-123"


@pytest.mark.asyncio
async def test_read_provider_by_user_id(db_session, user_with_provider):
    """Test querying provider by user_id."""
    provider = await user_with_provider("query@example.com")

    result = await db_session.execute(select(Provider).where(Provider.user_id == provider.user_id))
    assert result.scalar_one_or_none().id == provider.id


@pytest.mark.asyncio
async def test_provider_with_credentials(user_with_provider):
    """Test provider with credentials."""
    provider = await user_with_provider("creds@example.com", credentials="MD, PhD")
    assert provider.credentials == "MD, PhD"


@pytest.mark.asyncio
async def test_provider_with_languages(user_with_provider):
    """Test provider with languages."""
    langs = ["English", "Spanish", "French"]
    provider = await user_with_provider("lang@example.com", languages_spoken=langs)
    assert provider.languages_spoken == langs


@pytest.mark.asyncio
async def test_provider_with_insurances(user_with_provider):
    """Test provider with insurances."""
    insurances = ["Aetna", "Blue Cross"]
    provider = await user_with_provider("ins@example.com", accepted_insurances=insurances)
    assert provider.accepted_insurances == insurances


@pytest.mark.asyncio
async def test_provider_with_certifications(user_with_provider):
    """Test provider with certifications."""
    certs = ["Board Certified"]
    provider = await user_with_provider("cert@example.com", certifications=certs)
    assert provider.certifications == certs


@pytest.mark.asyncio
async def test_provider_accepting_new_patients(user_with_provider):
    """Test accepting new patients flag."""
    provider = await user_with_provider("accept@example.com", accepting_new_patients=False)
    assert provider.accepting_new_patients is False


@pytest.mark.asyncio
async def test_provider_years_of_experience(user_with_provider):
    """Test years of experience."""
    provider = await user_with_provider("exp@example.com", years_of_experience=15)
    assert provider.years_of_experience == 15


@pytest.mark.asyncio
async def test_provider_unique_user_id_constraint(db_session, user_factory, provider_factory):
    """Test duplicate user_id is rejected."""
    user = user_factory(email="unique@example.com", role="provider")
    db_session.add(user)
    await db_session.commit()

    db_session.add(provider_factory(user_id=user.id, license_number="LIC-001"))
    await db_session.commit()

    db_session.add(provider_factory(user_id=user.id, license_number="LIC-002"))
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_provider_unique_license_constraint(
    db_session, user_with_provider, user_factory, provider_factory
):
    """Test duplicate license is rejected."""
    await user_with_provider("prov1@example.com", license_number="LIC-SAME")

    user2 = user_factory(email="prov2@example.com", role="provider")
    db_session.add(user2)
    await db_session.commit()

    db_session.add(provider_factory(user_id=user2.id, license_number="LIC-SAME"))
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_update_provider(db_session, user_with_provider):
    """Test updating provider fields."""
    provider = await user_with_provider(
        "update@example.com", specialty="General", accepting_new_patients=True
    )

    provider.specialty = "Cardiology"
    provider.accepting_new_patients = False
    await db_session.commit()
    await db_session.refresh(provider)

    assert provider.specialty == "Cardiology"
    assert provider.accepting_new_patients is False


@pytest.mark.asyncio
async def test_provider_user_relationship(user_with_provider):
    """Test provider-user relationship."""
    provider = await user_with_provider("relation@example.com")
    assert provider.user.email == "relation@example.com"


@pytest.mark.asyncio
async def test_provider_repr(user_with_provider):
    """Test string representation."""
    provider = await user_with_provider(
        "repr@example.com", specialty="Neurology", license_number="LIC-REPR"
    )

    repr_str = repr(provider)
    assert "Neurology" in repr_str
    assert "LIC-REPR" in repr_str


@pytest.mark.asyncio
async def test_filter_providers_by_specialty(db_session, user_with_provider):
    """Test filtering by specialty."""
    await user_with_provider("cardio@example.com", specialty="Cardiology", license_number="L1")
    await user_with_provider("neuro@example.com", specialty="Neurology", license_number="L2")

    result = await db_session.execute(select(Provider).where(Provider.specialty == "Cardiology"))
    assert len(result.scalars().all()) == 1


@pytest.mark.asyncio
async def test_filter_providers_accepting_patients(db_session, user_with_provider):
    """Test filtering by accepting status."""
    await user_with_provider("yes@example.com", accepting_new_patients=True, license_number="L3")
    await user_with_provider("no@example.com", accepting_new_patients=False, license_number="L4")

    result = await db_session.execute(
        select(Provider).where(Provider.accepting_new_patients == True)
    )
    assert len(result.scalars().all()) == 1
