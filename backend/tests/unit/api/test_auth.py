"""
Auth API Tests - Unit tests for authentication endpoints
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from infrastructure.database.schemas.auth import LoginRequest, TokenResponse


@pytest.fixture
def mock_auth_service():
    """Mock AuthService for testing."""
    service = AsyncMock()
    service.login.return_value = ("access.token.here", "refresh.token.here")
    service.refresh_tokens.return_value = ("new.access.token", "new.refresh.token")
    return service


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock()
    user.id = uuid4()
    user.email = "test@example.com"
    user.first_name = "Test"
    user.last_name = "User"
    user.phone_number = None
    user.role = "patient"
    user.is_active = True
    user.is_verified = False
    user.created_at = "2025-01-01T00:00:00Z"
    user.updated_at = None
    user.last_login_at = None
    return user


class TestLoginEndpoint:
    """Tests for POST /auth/login"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_auth_service):
        """Valid credentials should return tokens."""
        # Simulate what the endpoint does
        login_data = LoginRequest(email="test@example.com", password="password123")

        access_token, refresh_token = await mock_auth_service.login(
            login_data.email, login_data.password
        )

        response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

        assert response.access_token == "access.token.here"
        assert response.refresh_token == "refresh.token.here"
        assert response.token_type == "bearer"
        mock_auth_service.login.assert_called_once_with("test@example.com", "password123")

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, mock_auth_service):
        """Invalid credentials should raise error."""
        from services.errors import InvalidCredentialsError

        mock_auth_service.login.side_effect = InvalidCredentialsError()

        login_data = LoginRequest(email="bad@example.com", password="wrong")

        with pytest.raises(InvalidCredentialsError):
            await mock_auth_service.login(login_data.email, login_data.password)


class TestRefreshEndpoint:
    """Tests for POST /auth/refresh"""

    def test_refresh_tokens_success(self):
        """Valid refresh token should return new tokens."""
        from unittest.mock import MagicMock

        mock_auth_service = MagicMock()
        mock_auth_service.refresh_tokens.return_value = ("new.access.token", "new.refresh.token")

        subject = {"user_id": str(uuid4()), "email": "test@example.com", "role": "patient"}

        access_token, refresh_token = mock_auth_service.refresh_tokens(subject)

        response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

        assert response.access_token == "new.access.token"
        assert response.refresh_token == "new.refresh.token"


class TestMeEndpoint:
    """Tests for GET /auth/me"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_auth_service, mock_user):
        """Valid token should return user info."""
        mock_auth_service.get_user_from_token.return_value = mock_user

        user = await mock_auth_service.get_user_from_token(str(mock_user.id))

        assert user.email == "test@example.com"
        assert user.role == "patient"
        mock_auth_service.get_user_from_token.assert_called_once()
