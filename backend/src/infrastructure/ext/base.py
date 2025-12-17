"""Base interface for external API's implementations."""

from abc import ABC, abstractmethod 
from typing import List, Optional
from pydantic import BaseModel

class ICD10Code(BaseModel):
    """Represents an ICD-10 code."""
    code: str
    description: str
    category: Optional[str] = None
    
class SymptomSearchResult(BaseModel):
    """Represents a symptom search result."""
    total_matches: int
    results: List[ICD10Code]
    
class ISymptomValidator(ABC):
    """Interface for symptom validation external API implementations."""
    
    @abstractmethod
    async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
        """Validates a symptom against the ICD-10 codes."""
        pass
    
    @abstractmethod
    async def search_symptoms(self, query: str, limit: int = 10) -> SymptomSearchResult:
        """Searches for symptoms matching the query string."""
        pass
    