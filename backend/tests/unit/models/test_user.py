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
        role="patient",
        email="test@example.com",
        first_name="Test",
        last_name="User"
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
        email = "test@example.com",
        role = "patient",
    )
    
    db_session.add(user)
    await db_session.commit()
    
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    found_user = result.scalar_one_or_none()
    
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == "test@example.com"