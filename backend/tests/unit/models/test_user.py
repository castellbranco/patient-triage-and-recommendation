""" 
Unit Tests for the User model.
"""

import asyncio
import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.patient import Patient
from app.infrastructure.database.models.provider import Provider

@pytest.mark.asyncio
async def test_create_user_sucess(db_session, user_factory):
    """Test successful creation of a User."""
    user = user_factory(
        role="patient",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    
    db_session.add(user)
    await db_session.flush()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"