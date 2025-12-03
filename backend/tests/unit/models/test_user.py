"""
Unit Tests for the User model.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from infrastructure.database.models.user import User


@pytest.mark.asyncio
async def test_create_user_success(db_session, user_factory):
    """Test successful creation of a User."""
    user = user_factory(
        role="patient", email="test@example.com", first_name="Test", last_name="User"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role == "patient"


@pytest.mark.asyncio
async def test_read_user_by_email(db_session, user_factory):
    """Test querying a user by email address."""
    user = user_factory(
        email="test@example.com",
        role="patient",
    )

    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    found_user = result.scalar_one_or_none()

    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_user_default_values(db_session, user_factory):
    """Test that default values are set correctly."""
    user = user_factory(email="defaults@example.com", role="patient")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_active is True
    assert user.is_verified is True
    assert user.last_login_at is None


@pytest.mark.asyncio
async def test_user_unique_email_constraint(db_session, user_factory):
    """Test that duplicate emails are rejected."""
    user1 = user_factory(email="duplicate@example.com", role="patient")
    user2 = user_factory(email="duplicate@example.com", role="provider")

    db_session.add(user1)
    await db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_with_phone_number(db_session, user_factory):
    """Test creating a user with optional phone number."""
    user = user_factory(email="phone@example.com", role="patient", phone_number="+1987654321")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.phone_number == "+1987654321"


@pytest.mark.asyncio
async def test_user_roles(db_session, user_factory):
    """Test creating users with different roles."""
    patient = user_factory(email="patient@example.com", role="patient")
    provider = user_factory(email="provider@example.com", role="provider")
    admin = user_factory(email="admin@example.com", role="admin")

    db_session.add_all([patient, provider, admin])
    await db_session.commit()

    assert patient.role == "patient"
    assert provider.role == "provider"
    assert admin.role == "admin"


@pytest.mark.asyncio
async def test_user_is_active_flag(db_session, user_factory):
    """Test creating an inactive user."""
    user = user_factory(email="inactive@example.com", role="patient", is_active=False)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_active is False


@pytest.mark.asyncio
async def test_user_is_verified_flag(db_session, user_factory):
    """Test creating an unverified user."""
    user = user_factory(email="unverified@example.com", role="patient", is_verified=False)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_verified is False


@pytest.mark.asyncio
async def test_update_user_email(db_session, user_factory):
    """Test updating a user's email."""
    user = user_factory(email="old@example.com", role="patient")

    db_session.add(user)
    await db_session.commit()

    user.email = "new@example.com"
    await db_session.commit()
    await db_session.refresh(user)

    assert user.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_name(db_session, user_factory):
    """Test updating a user's name."""
    user = user_factory(
        email="name@example.com", role="patient", first_name="Original", last_name="Name"
    )

    db_session.add(user)
    await db_session.commit()

    user.first_name = "Updated"
    user.last_name = "Person"
    await db_session.commit()
    await db_session.refresh(user)

    assert user.first_name == "Updated"
    assert user.last_name == "Person"


@pytest.mark.asyncio
async def test_user_repr(db_session, user_factory):
    """Test the string representation of a user."""
    user = user_factory(email="repr@example.com", role="admin")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    repr_str = repr(user)
    assert "repr@example.com" in repr_str
    assert "admin" in repr_str


@pytest.mark.asyncio
async def test_filter_users_by_role(db_session, user_factory):
    """Test filtering users by role."""
    user1 = user_factory(email="p1@example.com", role="patient")
    user2 = user_factory(email="p2@example.com", role="patient")
    user3 = user_factory(email="prov@example.com", role="provider")

    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.role == "patient"))
    patients = result.scalars().all()

    assert len(patients) == 2
    assert all(u.role == "patient" for u in patients)


@pytest.mark.asyncio
async def test_filter_users_by_is_active(db_session, user_factory):
    """Test filtering users by active status."""
    active = user_factory(email="active@example.com", role="patient", is_active=True)
    inactive = user_factory(email="inactive2@example.com", role="patient", is_active=False)

    db_session.add_all([active, inactive])
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.is_active == True))
    active_users = result.scalars().all()

    assert len(active_users) == 1
    assert active_users[0].email == "active@example.com"
