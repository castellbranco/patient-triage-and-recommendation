"""Unit tests for NLM API Client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, HTTPStatusError, TimeoutException, Response, Request

from src.infrastructure.ext.nlm_client import NLMClient
from src.infrastructure.ext.base import ICD10Code, SymptomSearchResult
from src.services.errors import (
    NLMAPITimeoutError,
    NLMAPIUnavailableError,
)


@pytest.fixture
def nlm_client():
    """Fixture for NLMClient instance."""
    return NLMClient(base_url="https://clinicaltables.nlm.nih.gov")


@pytest.fixture
def mock_httpx_client():
    """Fixture for mocked httpx AsyncClient."""
    return AsyncMock(spec=AsyncClient)


class TestNLMClientValidateSymptom:
    """Tests for validate_symptom method."""

    @pytest.mark.asyncio
    async def test_validate_symptom_success(self, nlm_client, mock_httpx_client):
        """Test successful symptom validation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            1,
            ["Headache"],
            None,
            [["Headache", "R51", "Headache"]]
        ]
        mock_httpx_client.get.return_value = mock_response

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await nlm_client.validate_symptom("headache")

        assert result is not None
        assert isinstance(result, ICD10Code)
        assert result.code == "R51"
        assert result.description == "Headache"

    @pytest.mark.asyncio
    async def test_validate_symptom_not_found(self, nlm_client, mock_httpx_client):
        """Test symptom not found returns None."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [0, [], None, []]
        mock_httpx_client.get.return_value = mock_response

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await nlm_client.validate_symptom("xyzabc123")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_symptom_timeout(self, nlm_client, mock_httpx_client):
        """Test timeout raises NLMAPITimeoutError."""
        mock_httpx_client.get.side_effect = TimeoutException("Timeout")

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            with pytest.raises(NLMAPITimeoutError):
                await nlm_client.validate_symptom("headache")

    @pytest.mark.asyncio
    async def test_validate_symptom_http_500(self, nlm_client, mock_httpx_client):
        """Test HTTP 500 error raises NLMAPIUnavailableError."""
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 500
        mock_request = MagicMock(spec=Request)
        
        mock_httpx_client.get.side_effect = HTTPStatusError(
            "Internal Server Error",
            request=mock_request,
            response=mock_response
        )

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            with pytest.raises(NLMAPIUnavailableError):
                await nlm_client.validate_symptom("headache")


class TestNLMClientSearchSymptoms:
    """Tests for search_symptoms method."""

    @pytest.mark.asyncio
    async def test_search_symptoms_success(self, nlm_client, mock_httpx_client):
        """Test successful symptom search."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            3,
            ["Headache", "Migraine", "Tension headache"],
            None,
            [
                ["Headache", "R51", "Headache"],
                ["Migraine", "G43", "Migraine"],
                ["Tension headache", "G44.209", "Tension-type headache"]
            ]
        ]
        mock_httpx_client.get.return_value = mock_response

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await nlm_client.search_symptoms("head", limit=10)

        assert isinstance(result, SymptomSearchResult)
        assert result.total_matches == 3
        assert len(result.results) == 3
        assert result.results[0].code == "R51"

    @pytest.mark.asyncio
    async def test_search_symptoms_empty(self, nlm_client, mock_httpx_client):
        """Test search with no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [0, [], None, []]
        mock_httpx_client.get.return_value = mock_response

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await nlm_client.search_symptoms("xyzabc")

        assert isinstance(result, SymptomSearchResult)
        assert result.total_matches == 0
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_search_symptoms_limit(self, nlm_client, mock_httpx_client):
        """Test that limit parameter is passed correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [0, [], None, []]
        mock_httpx_client.get.return_value = mock_response

        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            await nlm_client.search_symptoms("test", limit=5)

        call_args = mock_httpx_client.get.call_args
        assert call_args[1]["params"]["maxList"] == 5


@pytest.mark.integration
class TestNLMClientIntegration:
    """Integration tests with real NLM API."""

    @pytest.mark.asyncio
    async def test_real_api_validate_headache(self):
        """Test validation with real NLM API."""
        client = NLMClient()

        result = await client.validate_symptom("headache")

        assert result is not None
        assert result.code == "R51"

    @pytest.mark.asyncio
    async def test_real_api_search_chest(self):
        """Test search with real NLM API."""

        client = NLMClient()

        result = await client.search_symptoms("chest pain", limit=5)

        assert result.total_matches > 0
        assert len(result.results) > 0