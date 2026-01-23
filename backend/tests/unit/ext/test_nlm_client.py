"""Unit tests for NLM API Client."""
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

from infrastructure.ext.nlm_client import (
    NLMClient,
    MIN_QUERY_LENGTH,
    MAX_QUERY_LENGTH,
    MAX_RESULTS_LIMIT,
)
from infrastructure.ext.base import ICD10Code, SymptomSearchResult
from services.errors import (
    InvalidSymptomError,
    NLMAPIError,
    NLMAPITimeoutError,
    NLMAPIUnavailableError,
)


@pytest.fixture
def nlm_client():
    """Fixture for NLMClient instance."""
    return NLMClient(base_url="https://clinicaltables.nlm.nih.gov", timeout=5.0)


class TestNLMClientInit:
    """Tests for NLMClient initialization."""

    def test_init_with_defaults(self):
        """Test client initialization with default values."""
        client = NLMClient()
        assert client.base_url == "https://clinicaltables.nlm.nih.gov"
        assert client.timeout == 10.0
        assert client.client is None

    def test_init_with_custom_values(self):
        """Test client initialization with custom values."""
        client = NLMClient(base_url="https://custom.api.com/", timeout=30.0)
        assert client.base_url == "https://custom.api.com"  # Trailing slash removed
        assert client.timeout == 30.0

    def test_init_with_invalid_timeout_raises_error(self):
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be a positive number"):
            NLMClient(timeout=0)

        with pytest.raises(ValueError, match="Timeout must be a positive number"):
            NLMClient(timeout=-1)


class TestNLMClientContextManager:
    """Tests for context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_creates_client(self):
        """Test that async with creates the httpx client."""
        nlm = NLMClient()
        assert nlm.client is None
        
        async with nlm as client:
            assert client.client is not None
            assert isinstance(client.client, httpx.AsyncClient)
        
        # Client should be closed after exiting context
        assert nlm.client is None


class TestNLMClientSearchSymptoms:
    """Tests for search_symptoms method."""

    @pytest.mark.asyncio
    async def test_search_empty_query_raises_error(self, nlm_client):
        """Test that empty query raises InvalidSymptomError."""
        with pytest.raises(InvalidSymptomError):
            await nlm_client.search_symptoms("")

    @pytest.mark.asyncio
    async def test_search_whitespace_query_raises_error(self, nlm_client):
        """Test that whitespace-only query raises InvalidSymptomError."""
        with pytest.raises(InvalidSymptomError):
            await nlm_client.search_symptoms("   ")

    @pytest.mark.asyncio
    async def test_search_too_short_query_raises_error(self, nlm_client):
        """Test that query shorter than MIN_QUERY_LENGTH raises error."""
        with pytest.raises(InvalidSymptomError, match="at least"):
            await nlm_client.search_symptoms("a")  # Single character

    @pytest.mark.asyncio
    async def test_search_query_with_invalid_characters_raises_error(self, nlm_client):
        """Test that query with invalid characters raises error."""
        with pytest.raises(InvalidSymptomError, match="invalid characters"):
            await nlm_client.search_symptoms("test<script>")

    @pytest.mark.asyncio
    async def test_search_limit_clamped_to_bounds(self, nlm_client):
        """Test that limit is clamped to valid bounds."""
        mock_response_data = [0, [], {}, []]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        nlm_client.client = mock_client

        # Test with limit below minimum
        await nlm_client.search_symptoms("headache", limit=-5)
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["maxList"] == 1

        # Test with limit above maximum
        await nlm_client.search_symptoms("headache", limit=1000)
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["maxList"] == MAX_RESULTS_LIMIT

    @pytest.mark.asyncio
    async def test_search_symptoms_success(self, nlm_client):
        """Test successful symptom search with mocked response."""
        # Mock response matching NLM API format
        mock_response_data = [
            2,  # Total count
            ["12345", "67890"],  # Key IDs
            {  # Extra fields
                "icd10cm": [
                    [{"code": "R51", "name": "Headache"}],
                    [{"code": "G43.909", "name": "Migraine, unspecified"}]
                ]
            },
            [["Headache"], ["Migraine"]]  # Display fields
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        nlm_client.client = mock_client
        
        result = await nlm_client.search_symptoms("headache", limit=10)
        
        assert isinstance(result, SymptomSearchResult)
        assert result.total_matches == 2
        assert len(result.results) == 2
        assert result.results[0].code == "R51"
        assert result.results[0].description == "Headache"

    @pytest.mark.asyncio
    async def test_search_symptoms_no_results(self, nlm_client):
        """Test search with no matches."""
        mock_response_data = [0, [], {}, []]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        nlm_client.client = mock_client
        
        result = await nlm_client.search_symptoms("xyznonexistent123")
        
        assert result.total_matches == 0
        assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_search_symptoms_timeout(self, nlm_client):
        """Test that timeout raises NLMAPITimeoutError."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
        
        nlm_client.client = mock_client
        
        with pytest.raises(NLMAPITimeoutError):
            await nlm_client.search_symptoms("headache")

    @pytest.mark.asyncio
    async def test_search_symptoms_connection_error(self, nlm_client):
        """Test that connection error raises NLMAPIUnavailableError."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")
        
        nlm_client.client = mock_client
        
        with pytest.raises(NLMAPIUnavailableError):
            await nlm_client.search_symptoms("headache")

    @pytest.mark.asyncio
    async def test_search_symptoms_http_error(self, nlm_client):
        """Test that HTTP errors raise NLMAPIError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=mock_response
        )
        
        nlm_client.client = mock_client
        
        with pytest.raises(NLMAPIError):
            await nlm_client.search_symptoms("headache")


class TestNLMClientValidateSymptom:
    """Tests for validate_symptom method."""

    @pytest.mark.asyncio
    async def test_validate_empty_symptom_raises_error(self, nlm_client):
        """Test that empty symptom raises InvalidSymptomError."""
        with pytest.raises(InvalidSymptomError):
            await nlm_client.validate_symptom("")

    @pytest.mark.asyncio
    async def test_validate_symptom_returns_first_match(self, nlm_client):
        """Test that validate_symptom returns the first ICD-10 code."""
        mock_response_data = [
            2,
            ["12345", "67890"],
            {"icd10cm": [[{"code": "R07.9", "name": "Chest pain, unspecified"}], []]},
            [["Chest Pain"], ["Another condition"]]
        ]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        nlm_client.client = mock_client
        
        result = await nlm_client.validate_symptom("chest pain")
        
        assert result is not None
        assert result.code == "R07.9"
        assert result.description == "Chest pain, unspecified"

    @pytest.mark.asyncio
    async def test_validate_symptom_no_match_returns_none(self, nlm_client):
        """Test that no match returns None."""
        mock_response_data = [0, [], {}, []]
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        nlm_client.client = mock_client
        
        result = await nlm_client.validate_symptom("xyznonexistent")
        
        assert result is None


class TestNLMClientBatchValidation:
    """Tests for batch symptom validation."""

    @pytest.mark.asyncio
    async def test_validate_symptoms_batch(self, nlm_client):
        """Test batch validation of multiple symptoms."""
        # Setup mock to return different results for different calls
        call_count = 0
        
        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            
            if call_count == 1:  # First symptom - match
                mock_response.json.return_value = [
                    1, ["1"], {"icd10cm": [[{"code": "R51", "name": "Headache"}]]}, [["Headache"]]
                ]
            else:  # Second symptom - no match
                mock_response.json.return_value = [0, [], {}, []]
            
            return mock_response
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = mock_get
        
        nlm_client.client = mock_client
        
        results = await nlm_client.validate_symptoms_batch(["headache", "xyz123"])
        
        assert len(results) == 2
        assert results[0] is not None
        assert results[0].code == "R51"
        assert results[1] is None


class TestNLMClientResponseParsing:
    """Tests for response parsing edge cases."""

    def test_parse_response_with_question_mark_codes(self, nlm_client):
        """Test that codes with question marks are skipped."""
        # NLM uses ? as placeholder in some ICD-10 codes
        response_data = [
            1,
            ["12345"],
            {"icd10cm": [[{"code": "S72.001?", "name": "Fracture with placeholder"}]]},
            [["Some condition"]]
        ]

        result = nlm_client._parse_icd10_response(response_data)

        # Should skip codes with question marks
        assert len(result) == 0

    def test_parse_response_empty_data(self, nlm_client):
        """Test parsing empty response."""
        result = nlm_client._parse_icd10_response([])
        assert len(result) == 0

    def test_parse_response_malformed_data(self, nlm_client):
        """Test parsing malformed response."""
        result = nlm_client._parse_icd10_response([1, []])  # Missing fields
        assert len(result) == 0

    def test_parse_response_with_none_values(self, nlm_client):
        """Test parsing response with None values."""
        response_data = [
            1,
            ["12345"],
            None,  # extra_fields is None
            [["Some condition"]]
        ]
        result = nlm_client._parse_icd10_response(response_data)
        assert len(result) == 0

    def test_parse_response_with_invalid_icd_entry(self, nlm_client):
        """Test parsing response with non-dict icd entry."""
        response_data = [
            1,
            ["12345"],
            {"icd10cm": [["invalid_entry"]]},  # Entry is string, not dict
            [["Some condition"]]
        ]
        result = nlm_client._parse_icd10_response(response_data)
        assert len(result) == 0

    def test_parse_response_normalizes_code_to_uppercase(self, nlm_client):
        """Test that ICD-10 codes are normalized to uppercase."""
        response_data = [
            1,
            ["12345"],
            {"icd10cm": [[{"code": "r51", "name": "Headache"}]]},
            [["Headache"]]
        ]
        result = nlm_client._parse_icd10_response(response_data)
        assert len(result) == 1
        assert result[0].code == "R51"


class TestNLMClientInputSanitization:
    """Tests for input sanitization."""

    def test_sanitize_query_strips_whitespace(self, nlm_client):
        """Test that query whitespace is stripped."""
        result = nlm_client._sanitize_query("  headache  ")
        assert result == "headache"

    def test_sanitize_query_allows_medical_punctuation(self, nlm_client):
        """Test that valid medical punctuation is allowed."""
        # Test various valid inputs
        assert nlm_client._sanitize_query("chest pain") == "chest pain"
        assert nlm_client._sanitize_query("O'Brien's syndrome") == "O'Brien's syndrome"
        assert nlm_client._sanitize_query("pain (severe)") == "pain (severe)"

    def test_sanitize_query_rejects_special_characters(self, nlm_client):
        """Test that special characters are rejected."""
        with pytest.raises(InvalidSymptomError, match="invalid characters"):
            nlm_client._sanitize_query("test<script>alert(1)</script>")

        with pytest.raises(InvalidSymptomError, match="invalid characters"):
            nlm_client._sanitize_query("test;DROP TABLE")


class TestNLMClientBatchValidationEdgeCases:
    """Tests for batch validation edge cases."""

    @pytest.mark.asyncio
    async def test_batch_validation_empty_list(self, nlm_client):
        """Test batch validation with empty list."""
        results = await nlm_client.validate_symptoms_batch([])
        assert results == []

    @pytest.mark.asyncio
    async def test_batch_validation_handles_api_errors(self, nlm_client):
        """Test that batch validation handles API errors gracefully."""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")

        nlm_client.client = mock_client

        # Should return None for each symptom, not raise
        results = await nlm_client.validate_symptoms_batch(["headache", "nausea"])
        assert len(results) == 2
        assert all(r is None for r in results)