"""
Triage Schemas - Pydantic models for triage API request/response.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from infrastructure.database.models.triage import UrgencyLevel


# ============== ICD-10 Code Schemas ==============

class ICD10CodeSchema(BaseModel):
    """Schema for an ICD-10 code with description."""
    
    code: str = Field(..., description="ICD-10 code (e.g., 'R07.9')")
    description: str = Field(..., description="Description of the condition")
    category: Optional[str] = Field(None, description="Category/consumer name")
    
    model_config = {"from_attributes": True}


# ============== Triage Rule Schemas ==============

class TriageRuleBase(BaseModel):
    """Base schema for triage rules."""
    
    icd10_pattern: str = Field(
        ..., 
        min_length=1, 
        max_length=20,
        description="ICD-10 pattern with SQL wildcards (e.g., 'R07%')",
    )
    condition_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Human-readable condition name",
    )
    urgency_level: UrgencyLevel = Field(
        ..., 
        description="Urgency level for this condition",
    )
    recommended_specialty: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Recommended medical specialty",
    )
    description: Optional[str] = Field(
        None, 
        description="Additional notes about this rule",
    )
    is_active: bool = Field(
        True, 
        description="Whether this rule is active",
    )
    priority: int = Field(
        0, 
        ge=0, 
        description="Priority for rule matching (higher = more priority)",
    )


class TriageRuleCreate(TriageRuleBase):
    """Schema for creating a new triage rule."""
    pass


class TriageRuleUpdate(BaseModel):
    """Schema for updating a triage rule."""
    
    icd10_pattern: Optional[str] = Field(None, min_length=1, max_length=20)
    condition_name: Optional[str] = Field(None, min_length=1, max_length=255)
    urgency_level: Optional[UrgencyLevel] = None
    recommended_specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)


class TriageRuleResponse(TriageRuleBase):
    """Schema for triage rule response."""
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


# ============== Triage Analysis Schemas ==============

class TriageAnalyzeRequest(BaseModel):
    """Request schema for symptom analysis."""
    
    patient_id: UUID = Field(..., description="Patient ID to associate with the triage")
    symptoms: str = Field(
        ..., 
        min_length=3, 
        max_length=2000,
        description="Free-text description of symptoms",
        examples=["I have severe chest pain and difficulty breathing"],
    )
    additional_notes: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Additional context or notes",
    )


class MatchedRuleSchema(BaseModel):
    """Schema for a matched triage rule."""
    
    rule_id: UUID
    pattern: str
    condition_name: str
    urgency: UrgencyLevel
    specialty: str


class ProcessedSymptomSchema(BaseModel):
    """Schema for a processed symptom with ICD-10 code."""
    
    original_text: str
    icd10_code: Optional[str] = None
    icd10_description: Optional[str] = None
    matched: bool = False


class TriageAnalyzeResponse(BaseModel):
    """Response schema for symptom analysis."""
    
    triage_id: UUID = Field(..., description="ID of the created triage result")
    patient_id: UUID = Field(..., description="Patient ID")
    
    # Analysis results
    urgency_level: UrgencyLevel = Field(..., description="Final urgency assessment")
    recommended_specialty: str = Field(..., description="Recommended specialty")
    
    # Details
    processed_symptoms: List[ProcessedSymptomSchema] = Field(
        default_factory=list,
        description="Symptoms mapped to ICD-10 codes",
    )
    matched_rules: List[MatchedRuleSchema] = Field(
        default_factory=list,
        description="Triage rules that matched",
    )
    
    # Metadata
    confidence: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Confidence score (0.0 to 1.0)",
    )
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ============== Triage Result Schemas ==============

class TriageResultResponse(BaseModel):
    """Schema for triage result response."""
    
    id: UUID
    patient_id: UUID
    raw_symptoms: str
    processed_symptoms: list
    matched_rules: list
    urgency_level: UrgencyLevel
    recommended_specialty: str
    appointment_id: Optional[UUID] = None
    triage_notes: Optional[str] = None
    ai_confidence: Optional[float] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ============== Specialty Schemas ==============

class SpecialtyResponse(BaseModel):
    """Schema for specialty listing."""
    
    name: str = Field(..., description="Specialty name")
    conditions_count: int = Field(
        0, 
        description="Number of conditions mapped to this specialty",
    )


class SpecialtiesListResponse(BaseModel):
    """Response schema for specialty listing."""
    
    specialties: List[str] = Field(
        default_factory=list,
        description="List of available specialties",
    )
    total: int = Field(0, description="Total number of specialties")
