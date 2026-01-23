"""NLM (National Library of Medicine) API client for symptom validation.

This module implements the adapter for the NLM Clinical Tables API,
which provides ICD-10 code lookups for medical conditions.

API Documentation: https://clinicaltables.nlm.nih.gov/apidoc/conditions/v3/doc.html
"""
import logging
import re
from typing import List, Optional, Any

import httpx

from infrastructure.ext.base import (
    ISymptomValidator,
    ICD10Code,
    SymptomSearchResult,
)
from services.errors import (
    NLMAPIError,
    NLMAPITimeoutError,
    NLMAPIUnavailableError,
    InvalidSymptomError,
)

logger = logging.getLogger(__name__)

# Constants for validation
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 500
MAX_RESULTS_LIMIT = 500
DEFAULT_TIMEOUT = 10.0

# Pattern for sanitizing input - allow alphanumeric, spaces, and common medical punctuation
VALID_QUERY_PATTERN = re.compile(r"^[\w\s\-'.,()]+$", re.UNICODE)


class NLMClient(ISymptomValidator):
    """
    Client for NLM Clinical Tables API.

    This adapter connects to the National Library of Medicine's Clinical Tables
    API to validate symptoms and retrieve ICD-10 codes.

    Usage:
        async with NLMClient() as client:
            result = await client.search_symptoms("chest pain")
            code = await client.validate_symptom("headache")
    """

    # API endpoint for medical conditions
    CONDITIONS_ENDPOINT = "/api/conditions/v3/search"

    def __init__(
        self,
        base_url: str = "https://clinicaltables.nlm.nih.gov",
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the NLM API client.

        Args:
            base_url: Base URL for the NLM API
            timeout: Request timeout in seconds (must be positive)

        Raises:
            ValueError: If timeout is not positive
        """
        if timeout <= 0:
            raise ValueError("Timeout must be a positive number")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        
    @property
    def client(self) -> Optional[httpx.AsyncClient]:
        """Get the HTTP client (for backwards compatibility)."""
        return self._client

    @client.setter
    def client(self, value: Optional[httpx.AsyncClient]) -> None:
        """Set the HTTP client (for testing)."""
        self._client = value

    async def __aenter__(self) -> "NLMClient":
        """Called when entering 'async with' context."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Called when exiting 'async with' block."""
        await self.close()

    def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client exists, creating it if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Explicitly close the client connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @staticmethod
    def _sanitize_query(query: str) -> str:
        """
        Sanitize and validate the search query.

        Args:
            query: Raw query string

        Returns:
            Sanitized query string

        Raises:
            InvalidSymptomError: If query is invalid
        """
        if not query:
            raise InvalidSymptomError("Search query cannot be empty")

        cleaned = query.strip()

        if not cleaned:
            raise InvalidSymptomError("Search query cannot be empty")

        if len(cleaned) < MIN_QUERY_LENGTH:
            raise InvalidSymptomError(
                f"Search query must be at least {MIN_QUERY_LENGTH} characters"
            )

        if len(cleaned) > MAX_QUERY_LENGTH:
            raise InvalidSymptomError(
                f"Search query cannot exceed {MAX_QUERY_LENGTH} characters"
            )

        if not VALID_QUERY_PATTERN.match(cleaned):
            raise InvalidSymptomError(
                "Search query contains invalid characters"
            )

        return cleaned
    
    def _parse_icd10_response(self, data: List[Any]) -> List[ICD10Code]:
        """
        Parse the NLM API response into ICD10Code objects.

        NLM Response format:
        [
            total_count,           # [0] Total matches
            [key_ids],             # [1] Key IDs
            {"icd10cm": [...]},    # [2] Extra fields (icd10cm array)
            [[display_names]]      # [3] Display fields
        ]

        Args:
            data: Raw response from NLM API

        Returns:
            List of ICD10Code objects (empty list if parsing fails)
        """
        results: List[ICD10Code] = []

        # Validate response structure
        if not isinstance(data, list) or len(data) < 4:
            logger.warning("Invalid NLM API response format: insufficient data")
            return results

        try:
            key_ids = data[1] if isinstance(data[1], list) else []
            extra_fields = data[2] if isinstance(data[2], dict) else {}
            display_fields = data[3] if isinstance(data[3], list) else []

            # Get ICD-10 codes from extra fields
            icd10cm_list = extra_fields.get("icd10cm", [])

            for i, _ in enumerate(key_ids):
                # Get display name (consumer_name) with bounds checking
                display_name = "Unknown"
                if display_fields and i < len(display_fields):
                    field_entry = display_fields[i]
                    if isinstance(field_entry, list) and field_entry:
                        display_name = str(field_entry[0])

                # Get ICD-10 codes for this condition
                if i < len(icd10cm_list) and icd10cm_list[i]:
                    # icd10cm is an array of {code, name} objects
                    for icd_entry in icd10cm_list[i]:
                        if not isinstance(icd_entry, dict):
                            continue

                        code = str(icd_entry.get("code", "")).strip()
                        name = str(icd_entry.get("name", display_name)).strip()

                        # Skip empty codes or codes with question marks (placeholders)
                        if code and "?" not in code:
                            results.append(
                                ICD10Code(
                                    code=code,
                                    description=name or display_name,
                                    category=display_name,
                                )
                            )
                            break  # Take only the first valid code per condition

        except (TypeError, IndexError, KeyError) as e:
            logger.warning(f"Error parsing NLM API response: {e}")
            return []

        return results
    
    async def search_symptoms(self, query: str, limit: int = 10) -> SymptomSearchResult:
        """
        Search for symptoms/conditions matching the query string.

        Args:
            query: Search term (e.g., "chest pain", "headache")
            limit: Maximum number of results (1-500, defaults to 10)

        Returns:
            SymptomSearchResult with matching ICD-10 codes

        Raises:
            InvalidSymptomError: If query is empty or invalid
            NLMAPITimeoutError: If request times out
            NLMAPIUnavailableError: If API is unreachable
            NLMAPIError: For other API errors
        """
        # Validate and sanitize input
        sanitized_query = self._sanitize_query(query)

        # Validate limit bounds
        if limit < 1:
            limit = 1
        elif limit > MAX_RESULTS_LIMIT:
            limit = MAX_RESULTS_LIMIT

        client = self._ensure_client()

        # Build request parameters
        params = {
            "terms": sanitized_query,
            "maxList": limit,
            "df": "consumer_name",  # Display field
            "ef": "icd10cm",  # Extra fields - returns array of {code, name}
        }

        url = f"{self.base_url}{self.CONDITIONS_ENDPOINT}"

        try:
            logger.debug("NLM API request: %s with query length %d", url, len(sanitized_query))
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.debug("NLM API returned %d results", data[0] if data else 0)

            # Parse response with validation
            total_count = 0
            if isinstance(data, list) and data and isinstance(data[0], int):
                total_count = data[0]

            icd10_codes = self._parse_icd10_response(data)

            return SymptomSearchResult(
                total_matches=total_count,
                results=icd10_codes,
            )

        except httpx.TimeoutException as e:
            logger.error("NLM API timeout for query: %s", sanitized_query[:50])
            raise NLMAPITimeoutError() from e

        except httpx.ConnectError as e:
            logger.error("NLM API connection error: %s", str(e)[:100])
            raise NLMAPIUnavailableError() from e

        except httpx.HTTPStatusError as e:
            logger.error("NLM API HTTP error: %d", e.response.status_code)
            raise NLMAPIError(
                f"NLM API returned status {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e

        except (ValueError, TypeError, KeyError) as e:
            logger.error("NLM API response parsing error: %s", str(e)[:100])
            raise NLMAPIError(f"Invalid response from NLM API: {str(e)}") from e

        except Exception as e:
            logger.error("NLM API unexpected error: %s", str(e)[:100])
            raise NLMAPIError(f"Unexpected error: {str(e)}") from e
    
    async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
        """
        Validate a symptom and return the best matching ICD-10 code.

        This method searches for the symptom and returns the first
        (most relevant) matching ICD-10 code.

        Args:
            symptom: Symptom text to validate (e.g., "severe headache")

        Returns:
            ICD10Code if a match is found, None otherwise

        Raises:
            InvalidSymptomError: If symptom is empty or invalid
            NLMAPITimeoutError: If request times out
            NLMAPIUnavailableError: If API is unreachable
            NLMAPIError: For other API errors
        """
        # Input validation happens in search_symptoms via _sanitize_query
        # Search with limit of 5 to get best matches
        result = await self.search_symptoms(symptom, limit=5)

        if result.results:
            return result.results[0]

        return None
    
    async def validate_symptoms_batch(
        self,
        symptoms: List[str],
    ) -> List[Optional[ICD10Code]]:
        """
        Validate multiple symptoms in batch.

        Args:
            symptoms: List of symptom texts to validate

        Returns:
            List of ICD10Code objects (or None for non-matches/errors).
            The returned list maintains the same order as the input.
        """
        if not symptoms:
            return []

        results: List[Optional[ICD10Code]] = []
        for symptom in symptoms:
            try:
                code = await self.validate_symptom(symptom)
                results.append(code)
            except InvalidSymptomError:
                # Invalid input - return None for this symptom
                results.append(None)
            except (NLMAPIError, NLMAPITimeoutError, NLMAPIUnavailableError) as e:
                # API errors - log and continue with None
                logger.warning("Failed to validate symptom '%s': %s", symptom[:30], str(e)[:50])
                results.append(None)

        return results