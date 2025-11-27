""" 
Unit Tests for the User model.
"""

import asyncio
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from infrastructure.database.models.user import User
from infrastructure.database.models.patient import Patient
from infrastructure.database.models.provider import Provider

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

