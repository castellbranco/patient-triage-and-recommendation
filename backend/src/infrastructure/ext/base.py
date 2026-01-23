"""Base interface for external API implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ICD10Code(BaseModel):
    """
    Represents an ICD-10 code with description.

    ICD-10 codes follow a specific format: a letter followed by digits,
    optionally with a decimal point and more digits.
    """

    code: str = Field(
        ...,
        min_length=3,
        max_length=10,
        description="ICD-10 code (e.g., 'R07.9', 'G43.909')",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the condition",
    )
    category: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Category or consumer-friendly name",
    )

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Validate that code has a reasonable ICD-10 format."""
        v = v.strip().upper()
        if not v:
            raise ValueError("ICD-10 code cannot be empty")
        # Basic format check: starts with letter, contains alphanumeric and dots
        if not v[0].isalpha():
            raise ValueError("ICD-10 code must start with a letter")
        return v

    model_config = {"frozen": True}  # Make instances immutable


class SymptomSearchResult(BaseModel):
    """Represents a symptom search result from an external API."""

    total_matches: int = Field(
        ...,
        ge=0,
        description="Total number of matches found",
    )
    results: List[ICD10Code] = Field(
        default_factory=list,
        description="List of matching ICD-10 codes",
    )

    model_config = {"frozen": True}


class ISymptomValidator(ABC):
    """
    Interface for symptom validation external API implementations.

    Implementations should handle:
    - Input validation and sanitization
    - Rate limiting and retries
    - Proper error handling with specific exception types
    """

    @abstractmethod
    async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
        """
        Validate a symptom and return the best matching ICD-10 code.

        Args:
            symptom: Symptom text to validate

        Returns:
            ICD10Code if a match is found, None otherwise

        Raises:
            InvalidSymptomError: If symptom text is invalid
            ExternalAPIError: If the external API fails
        """
        pass

    @abstractmethod
    async def search_symptoms(self, query: str, limit: int = 10) -> SymptomSearchResult:
        """
        Search for symptoms matching the query string.

        Args:
            query: Search term
            limit: Maximum number of results

        Returns:
            SymptomSearchResult with matching ICD-10 codes

        Raises:
            InvalidSymptomError: If query is invalid
            ExternalAPIError: If the external API fails
        """
        pass
    