"""NLM (National Library of Medicine) API client for symptom validation.

This module implements the adapter for the NLM Clinical Tables API,
which provides ICD-10 code lookups for medical conditions.

API Documentation: https://clinicaltables.nlm.nih.gov/apidoc/conditions/v3/doc.html
"""
import logging
from typing import List, Optional

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
        timeout: float = 10.0,
    ):
        """
        Initialize the NLM API client.
        
        Args:
            base_url: Base URL for the NLM API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self) -> "NLMClient":
        """Called when entering 'async with' context."""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Called when exiting 'async with' block."""
        if self.client:
            await self.client.aclose()
            self.client = None
            
    def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client exists, creating it if needed."""
        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client
    
    async def close(self) -> None:
        """Explicitly close the client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    def _parse_icd10_response(self, data: list) -> List[ICD10Code]:
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
            List of ICD10Code objects
        """
        results = []
        
        if len(data) < 4:
            return results
            
        total_count = data[0]
        key_ids = data[1]
        extra_fields = data[2] if data[2] else {}
        display_fields = data[3]
        
        # Get ICD-10 codes from extra fields
        icd10cm_list = extra_fields.get("icd10cm", [])
        
        for i, key_id in enumerate(key_ids):
            # Get display name (consumer_name)
            display_name = display_fields[i][0] if display_fields and i < len(display_fields) else "Unknown"
            
            # Get ICD-10 codes for this condition
            if i < len(icd10cm_list) and icd10cm_list[i]:
                # icd10cm is an array of {code, name} objects
                for icd_entry in icd10cm_list[i]:
                    if isinstance(icd_entry, dict):
                        code = icd_entry.get("code", "")
                        name = icd_entry.get("name", display_name)
                        
                        # Skip codes with question marks (placeholders)
                        if code and "?" not in code:
                            results.append(ICD10Code(
                                code=code,
                                description=name,
                                category=display_name,
                            ))
                            break  # Take only the first valid code per condition
            
        return results
    
    async def search_symptoms(self, query: str, limit: int = 10) -> SymptomSearchResult:
        """
        Search for symptoms/conditions matching the query string.
        
        Args:
            query: Search term (e.g., "chest pain", "headache")
            limit: Maximum number of results (max 500)
            
        Returns:
            SymptomSearchResult with matching ICD-10 codes
            
        Raises:
            InvalidSymptomError: If query is empty
            NLMAPITimeoutError: If request times out
            NLMAPIUnavailableError: If API is unreachable
            NLMAPIError: For other API errors
        """
        if not query or not query.strip():
            raise InvalidSymptomError("Search query cannot be empty")
        
        client = self._ensure_client()
        
        # Build request parameters
        params = {
            "terms": query.strip(),
            "maxList": min(limit, 500),  # API max is 500
            "df": "consumer_name",  # Display field
            "ef": "icd10cm",  # Extra fields - returns array of {code, name}
        }
        
        url = f"{self.base_url}{self.CONDITIONS_ENDPOINT}"
        
        try:
            logger.debug(f"NLM API request: {url} with params {params}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"NLM API response: {data}")
            
            # Parse response
            total_count = data[0] if data else 0
            icd10_codes = self._parse_icd10_response(data)
            
            return SymptomSearchResult(
                total_matches=total_count,
                results=icd10_codes,
            )
            
        except httpx.TimeoutException as e:
            logger.error(f"NLM API timeout: {e}")
            raise NLMAPITimeoutError() from e
            
        except httpx.ConnectError as e:
            logger.error(f"NLM API connection error: {e}")
            raise NLMAPIUnavailableError() from e
            
        except httpx.HTTPStatusError as e:
            logger.error(f"NLM API HTTP error: {e.response.status_code}")
            raise NLMAPIError(
                f"NLM API returned status {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e
            
        except Exception as e:
            logger.error(f"NLM API unexpected error: {e}")
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
            InvalidSymptomError: If symptom is empty
            NLMAPITimeoutError: If request times out
            NLMAPIUnavailableError: If API is unreachable
            NLMAPIError: For other API errors
        """
        if not symptom or not symptom.strip():
            raise InvalidSymptomError("Symptom cannot be empty")
        
        # Search with limit of 1 to get best match
        result = await self.search_symptoms(symptom.strip(), limit=5)
        
        if result.results:
            return result.results[0]
        
        return None
    
    async def validate_symptoms_batch(
        self, 
        symptoms: List[str]
    ) -> List[Optional[ICD10Code]]:
        """
        Validate multiple symptoms in batch.
        
        Args:
            symptoms: List of symptom texts to validate
            
        Returns:
            List of ICD10Code objects (or None for non-matches)
        """
        results = []
        for symptom in symptoms:
            try:
                code = await self.validate_symptom(symptom)
                results.append(code)
            except InvalidSymptomError:
                results.append(None)
        return results