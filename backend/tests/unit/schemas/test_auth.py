"""
Auth Schema Tests - Simple validation tests for auth DTOs
"""

import pytest
from pydantic import ValidationError

from infrastructure.database.schemas.auth import LoginRequest, TokenResponse


class TestLoginRequest:
    """Tests for LoginRequest schema."""

    def test_valid_login_request(self):
        """Valid email and password should work."""
        data = LoginRequest(email="test@example.com", password="password123")

        assert data.email == "test@example.com"
        assert data.password == "password123"

    def test_invalid_email_format(self):
        """Invalid email format should raise ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="password123")

    def test_empty_password_rejected(self):
        """Empty password should raise ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="")

    def test_missing_email_rejected(self):
        """Missing email should raise ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")

    def test_missing_password_rejected(self):
        """Missing password should raise ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")


class TestTokenResponse:
    """Tests for TokenResponse schema."""

    def test_valid_token_response(self):
        """Valid tokens should work."""
        data = TokenResponse(
            access_token="access.token.here",
            refresh_token="refresh.token.here",
        )

        assert data.access_token == "access.token.here"
        assert data.refresh_token == "refresh.token.here"
        assert data.token_type == "bearer"

    def test_custom_token_type(self):
        """Custom token_type should work."""
        data = TokenResponse(
            access_token="access",
            refresh_token="refresh",
            token_type="custom",
        )

        assert data.token_type == "custom"

    def test_missing_access_token_rejected(self):
        """Missing access_token should raise ValidationError."""
        with pytest.raises(ValidationError):
            TokenResponse(refresh_token="refresh.token.here")

    def test_missing_refresh_token_rejected(self):
        """Missing refresh_token should raise ValidationError."""
        with pytest.raises(ValidationError):
            TokenResponse(access_token="access.token.here")
