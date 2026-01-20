"""
Triage API Module - Routes for triage/symptom analysis endpoints.
"""

from typing import List
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from infrastructure.api.utils import Pagination
from infrastructure.database.schemas.triage import (
    TriageAnalyzeRequest,
    TriageAnalyzeResponse,
    TriageResultResponse,
    TriageRuleCreate,
    TriageRuleResponse,
    TriageRuleUpdate,
    SpecialtiesListResponse,
)
from services.triage import TriageService
from dishka.integrations.fastapi import FromDishka


router = APIRouter(prefix="/triage", tags=["Triage"], route_class=DishkaRoute)

# Type alias for dependency injection
TriageServiceDep = FromDishka[TriageService]


# ============== Symptom Analysis Endpoints ==============

@router.post(
    "/analyze",
    response_model=TriageAnalyzeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze patient symptoms",
    responses={
        201: {"description": "Symptoms analyzed successfully"},
        404: {"description": "Patient not found"},
        503: {"description": "NLM API unavailable"},
    },
)
async def analyze_symptoms(
    request: TriageAnalyzeRequest,
    service: TriageServiceDep,
) -> TriageAnalyzeResponse:
    """
    Analyze patient symptoms and determine urgency level.
    
    This endpoint:
    1. Parses the free-text symptoms
    2. Validates against NLM API for ICD-10 codes
    3. Matches against triage rules
    4. Returns urgency level and recommended specialty
    
    **Example Request:**
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "symptoms": "severe chest pain and difficulty breathing"
    }
    ```
    """
    return await service.analyze_symptoms(request)


@router.get(
    "/results/{triage_id}",
    response_model=TriageResultResponse,
    summary="Get triage result",
    responses={
        200: {"description": "Triage result retrieved"},
        404: {"description": "Triage result not found"},
    },
)
async def get_triage_result(
    triage_id: UUID,
    service: TriageServiceDep,
) -> TriageResultResponse:
    """Get a specific triage result by ID."""
    result = await service.get_triage_result(triage_id)
    if not result:
        from services.errors import NotFoundError
        raise NotFoundError(f"Triage result {triage_id} not found")
    return TriageResultResponse.model_validate(result)


@router.get(
    "/patient/{patient_id}/history",
    response_model=List[TriageResultResponse],
    summary="Get patient triage history",
    responses={
        200: {"description": "Triage history retrieved"},
        404: {"description": "Patient not found"},
    },
)
async def get_patient_triage_history(
    patient_id: UUID,
    service: TriageServiceDep,
    limit: int = 10,
) -> List[TriageResultResponse]:
    """Get triage history for a specific patient."""
    results = await service.get_patient_triage_history(patient_id, limit)
    return [TriageResultResponse.model_validate(r) for r in results]


# ============== Specialty Endpoints ==============

@router.get(
    "/specialties",
    response_model=SpecialtiesListResponse,
    summary="List available specialties",
    responses={
        200: {"description": "Specialties retrieved"},
    },
)
async def list_specialties(
    service: TriageServiceDep,
) -> SpecialtiesListResponse:
    """
    Get list of all available medical specialties.
    
    Returns specialties derived from active triage rules.
    """
    specialties = await service.get_available_specialties()
    return SpecialtiesListResponse(
        specialties=specialties,
        total=len(specialties),
    )


# ============== Triage Rule Management (Admin) ==============

@router.get(
    "/rules",
    response_model=List[TriageRuleResponse],
    summary="List triage rules",
    responses={
        200: {"description": "Triage rules retrieved"},
    },
)
async def list_triage_rules(
    service: TriageServiceDep,
) -> List[TriageRuleResponse]:
    """
    List all active triage rules.
    
    Used by administrators to view current triage configuration.
    """
    rules = await service.triage_rule_repo.get_active_rules()
    return [TriageRuleResponse.model_validate(r) for r in rules]


@router.post(
    "/rules",
    response_model=TriageRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create triage rule",
    responses={
        201: {"description": "Triage rule created"},
    },
)
async def create_triage_rule(
    rule_data: TriageRuleCreate,
    service: TriageServiceDep,
) -> TriageRuleResponse:
    """
    Create a new triage rule.
    
    **Example:**
    ```json
    {
        "icd10_pattern": "R07%",
        "condition_name": "Chest Pain",
        "urgency_level": "high",
        "recommended_specialty": "Cardiology"
    }
    ```
    """
    from infrastructure.database.models.triage import TriageRule
    
    rule = TriageRule(
        icd10_pattern=rule_data.icd10_pattern,
        condition_name=rule_data.condition_name,
        urgency_level=rule_data.urgency_level,
        recommended_specialty=rule_data.recommended_specialty,
        description=rule_data.description,
        is_active=rule_data.is_active,
        priority=rule_data.priority,
    )
    
    created_rule = await service.triage_rule_repo.create(rule)
    return TriageRuleResponse.model_validate(created_rule)


@router.patch(
    "/rules/{rule_id}",
    response_model=TriageRuleResponse,
    summary="Update triage rule",
    responses={
        200: {"description": "Triage rule updated"},
        404: {"description": "Triage rule not found"},
    },
)
async def update_triage_rule(
    rule_id: UUID,
    rule_data: TriageRuleUpdate,
    service: TriageServiceDep,
) -> TriageRuleResponse:
    """Update an existing triage rule."""
    rule = await service.triage_rule_repo.get_by_id(rule_id)
    if not rule:
        from services.errors import NotFoundError
        raise NotFoundError(f"Triage rule {rule_id} not found")
    
    # Update only provided fields
    update_data = rule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    updated_rule = await service.triage_rule_repo.update(rule)
    return TriageRuleResponse.model_validate(updated_rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete triage rule",
    responses={
        204: {"description": "Triage rule deleted"},
        404: {"description": "Triage rule not found"},
    },
)
async def delete_triage_rule(
    rule_id: UUID,
    service: TriageServiceDep,
) -> None:
    """
    Delete a triage rule.
    
    Consider using PATCH to set is_active=false for soft deactivation.
    """
    rule = await service.triage_rule_repo.get_by_id(rule_id)
    if not rule:
        from services.errors import NotFoundError
        raise NotFoundError(f"Triage rule {rule_id} not found")
    
    await service.triage_rule_repo.delete(rule)
