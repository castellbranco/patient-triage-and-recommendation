"""
Triage Service Module

Core business logic for the triage engine. This service:
1. Receives free-text symptoms from patients
2. Validates symptoms against NLM API to get ICD-10 codes
3. Matches ICD-10 codes against triage rules
4. Determines urgency level and recommends specialty
5. Stores the triage result
"""

import logging
import re
from typing import List, Optional, Tuple
from uuid import UUID

from infrastructure.database.models.triage import (
    TriageResult,
    TriageRule,
    UrgencyLevel,
)
from infrastructure.database.schemas.triage import (
    TriageAnalyzeRequest,
    TriageAnalyzeResponse,
    ProcessedSymptomSchema,
    MatchedRuleSchema,
)
from infrastructure.ext.base import ISymptomValidator, ICD10Code
from infrastructure.repo.triage import TriageRuleRepository, TriageResultRepository
from infrastructure.repo.patient import PatientRepository
from services.errors import (
    PatientNotFoundError,
    NLMAPIError,
    NLMAPITimeoutError,
    NLMAPIUnavailableError,
    InvalidSymptomError,
    TriageResultNotFoundError,
)

logger = logging.getLogger(__name__)


# Default fallback when no rules match
DEFAULT_URGENCY = UrgencyLevel.MEDIUM
DEFAULT_SPECIALTY = "General Practice"

# Symptom parsing constants
MIN_SYMPTOM_LENGTH = 2
MAX_SYMPTOMS_PER_REQUEST = 20
SYMPTOM_DELIMITERS = re.compile(r'[,;]|\band\b|\balso\b|\bwith\b', re.IGNORECASE)


class TriageService:
    """
    Service for patient triage and symptom analysis.

    This is the "brain" of the triage engine that:
    - Parses free-text symptoms
    - Calls NLM API to get standardized ICD-10 codes
    - Matches against triage rules
    - Determines the highest urgency level
    - Recommends the appropriate specialty
    """

    def __init__(
        self,
        triage_rule_repo: TriageRuleRepository,
        triage_result_repo: TriageResultRepository,
        patient_repo: PatientRepository,
        nlm_client: ISymptomValidator,
    ):
        if triage_rule_repo is None:
            raise ValueError("triage_rule_repo cannot be None")
        if triage_result_repo is None:
            raise ValueError("triage_result_repo cannot be None")
        if patient_repo is None:
            raise ValueError("patient_repo cannot be None")
        if nlm_client is None:
            raise ValueError("nlm_client cannot be None")

        self.triage_rule_repo = triage_rule_repo
        self.triage_result_repo = triage_result_repo
        self.patient_repo = patient_repo
        self.nlm_client = nlm_client
    
    def _parse_symptoms(self, text: str) -> List[str]:
        """
        Parse free-text into individual symptom phrases.

        Splits on common delimiters like commas, 'and', semicolons.

        Args:
            text: Free-text symptom description

        Returns:
            List of individual symptom phrases (max MAX_SYMPTOMS_PER_REQUEST)
        """
        if not text:
            return []

        # Normalize the text
        normalized = text.strip().lower()

        if not normalized:
            return []

        # Split on common delimiters
        # "chest pain and headache, nausea" -> ["chest pain", "headache", "nausea"]
        symptoms = SYMPTOM_DELIMITERS.split(normalized)

        # Clean up each symptom
        cleaned: List[str] = []
        for symptom in symptoms:
            symptom = symptom.strip()
            # Skip very short fragments that are likely parsing artifacts
            if symptom and len(symptom) >= MIN_SYMPTOM_LENGTH:
                cleaned.append(symptom)
                # Limit number of symptoms to prevent abuse
                if len(cleaned) >= MAX_SYMPTOMS_PER_REQUEST:
                    logger.warning(
                        "Symptom limit reached, truncating to %d symptoms",
                        MAX_SYMPTOMS_PER_REQUEST,
                    )
                    break

        # If no splits occurred, treat the whole text as one symptom
        if not cleaned and len(normalized) >= MIN_SYMPTOM_LENGTH:
            cleaned = [normalized]

        return cleaned
    
    async def _validate_symptoms_with_nlm(
        self,
        symptoms: List[str],
    ) -> List[Tuple[str, Optional[ICD10Code]]]:
        """
        Validate each symptom against NLM API.

        Args:
            symptoms: List of symptom phrases

        Returns:
            List of (symptom_text, ICD10Code or None) tuples.
            Order is preserved to match input.
        """
        if not symptoms:
            return []

        results: List[Tuple[str, Optional[ICD10Code]]] = []

        for symptom in symptoms:
            try:
                icd10_code = await self.nlm_client.validate_symptom(symptom)
                results.append((symptom, icd10_code))
            except InvalidSymptomError as e:
                # Input validation failed - log at debug level
                logger.debug("Invalid symptom '%s': %s", symptom[:30], str(e))
                results.append((symptom, None))
            except (NLMAPIError, NLMAPITimeoutError, NLMAPIUnavailableError) as e:
                # API errors - log at warning level
                logger.warning("NLM API error for symptom '%s': %s", symptom[:30], str(e)[:50])
                results.append((symptom, None))
            except Exception as e:
                # Unexpected errors - log at error level but don't fail the whole request
                logger.error("Unexpected error validating symptom '%s': %s", symptom[:30], str(e)[:50])
                results.append((symptom, None))

        return results
    
    @staticmethod
    def _get_urgency_order() -> dict:
        """Return urgency level ordering (higher = more urgent)."""
        return {
            UrgencyLevel.LOW: 1,
            UrgencyLevel.MEDIUM: 2,
            UrgencyLevel.HIGH: 3,
            UrgencyLevel.EMERGENCY: 4,
        }

    def _determine_urgency(
        self,
        matched_rules: List[TriageRule],
    ) -> Tuple[UrgencyLevel, str]:
        """
        Determine the highest urgency level from matched rules.

        Returns the urgency and specialty from the highest-priority rule.

        Args:
            matched_rules: List of matched triage rules

        Returns:
            Tuple of (UrgencyLevel, recommended_specialty)
        """
        if not matched_rules:
            return DEFAULT_URGENCY, DEFAULT_SPECIALTY

        urgency_order = self._get_urgency_order()

        # Find the rule with highest urgency (rules are already sorted by priority)
        highest_rule = max(
            matched_rules,
            key=lambda r: (urgency_order.get(r.urgency_level, 0), r.priority),
        )

        return highest_rule.urgency_level, highest_rule.recommended_specialty
    
    @staticmethod
    def _calculate_confidence(
        total_symptoms: int,
        matched_symptoms: int,
        matched_rules: int,
    ) -> float:
        """
        Calculate a confidence score for the triage result.

        Based on:
        - How many symptoms were matched to ICD-10 codes
        - How many rules were matched

        Args:
            total_symptoms: Total number of symptoms parsed
            matched_symptoms: Number of symptoms matched to ICD-10 codes
            matched_rules: Number of triage rules matched

        Returns:
            Score between 0.0 and 1.0
        """
        if total_symptoms <= 0:
            return 0.0

        # Ensure non-negative inputs
        matched_symptoms = max(0, matched_symptoms)
        matched_rules = max(0, matched_rules)

        # Symptom match ratio (50% weight)
        symptom_ratio = min(matched_symptoms / total_symptoms, 1.0)

        # Rule match bonus (50% weight, maxes out at 3+ rules)
        rule_bonus = min(matched_rules / 3.0, 1.0)

        confidence = (symptom_ratio * 0.5) + (rule_bonus * 0.5)

        return round(confidence, 2)
    
    async def analyze_symptoms(
        self, 
        request: TriageAnalyzeRequest
    ) -> TriageAnalyzeResponse:
        """
        Analyze patient symptoms and determine urgency.
        
        This is the main entry point for the triage engine.
        
        Args:
            request: TriageAnalyzeRequest with patient_id and symptoms
            
        Returns:
            TriageAnalyzeResponse with urgency, specialty, and details
            
        Raises:
            PatientNotFoundError: If patient doesn't exist
        """
        # 1. Validate patient exists
        patient = await self.patient_repo.get_by_id(request.patient_id)
        if not patient:
            raise PatientNotFoundError(str(request.patient_id))
        
        # 2. Parse symptoms from free text
        symptom_phrases = self._parse_symptoms(request.symptoms)
        logger.info(f"Parsed {len(symptom_phrases)} symptoms from input")
        
        # 3. Validate each symptom with NLM API
        validated_symptoms = await self._validate_symptoms_with_nlm(symptom_phrases)
        
        # 4. Build processed symptoms list and extract ICD-10 codes
        processed_symptoms: List[ProcessedSymptomSchema] = []
        icd10_codes: List[str] = []
        matched_count = 0
        
        for symptom_text, icd10_code in validated_symptoms:
            if icd10_code:
                processed_symptoms.append(ProcessedSymptomSchema(
                    original_text=symptom_text,
                    icd10_code=icd10_code.code,
                    icd10_description=icd10_code.description,
                    matched=True,
                ))
                icd10_codes.append(icd10_code.code)
                matched_count += 1
            else:
                processed_symptoms.append(ProcessedSymptomSchema(
                    original_text=symptom_text,
                    matched=False,
                ))
        
        # 5. Find matching triage rules
        matched_rules = await self.triage_rule_repo.find_matching_rules(icd10_codes)
        logger.info(f"Found {len(matched_rules)} matching triage rules")
        
        # 6. Determine urgency level and specialty
        urgency_level, recommended_specialty = self._determine_urgency(matched_rules)
        
        # 7. Calculate confidence
        confidence = self._calculate_confidence(
            len(symptom_phrases), 
            matched_count, 
            len(matched_rules)
        )
        
        # 8. Build matched rules response
        matched_rules_response: List[MatchedRuleSchema] = [
            MatchedRuleSchema(
                rule_id=rule.id,
                pattern=rule.icd10_pattern,
                condition_name=rule.condition_name,
                urgency=rule.urgency_level,
                specialty=rule.recommended_specialty,
            )
            for rule in matched_rules
        ]
        
        # 9. Create and save triage result
        triage_result = TriageResult(
            patient_id=request.patient_id,
            raw_symptoms=request.symptoms,
            processed_symptoms=[s.model_dump() for s in processed_symptoms],
            matched_rules=[r.model_dump(mode="json") for r in matched_rules_response],
            urgency_level=urgency_level,
            recommended_specialty=recommended_specialty,
            triage_notes=request.additional_notes,
            ai_confidence=confidence,
        )
        
        saved_result = await self.triage_result_repo.create(triage_result)
        
        # 10. Return response
        return TriageAnalyzeResponse(
            triage_id=saved_result.id,
            patient_id=saved_result.patient_id,
            urgency_level=saved_result.urgency_level,
            recommended_specialty=saved_result.recommended_specialty,
            processed_symptoms=processed_symptoms,
            matched_rules=matched_rules_response,
            confidence=confidence,
            created_at=saved_result.created_at,
        )
    
    async def get_triage_result(self, triage_id: UUID) -> Optional[TriageResult]:
        """Get a specific triage result by ID."""
        return await self.triage_result_repo.get_by_id(triage_id)

    async def get_triage_result_or_raise(self, triage_id: UUID) -> TriageResult:
        """
        Get a specific triage result by ID, raising if not found.

        Args:
            triage_id: UUID of the triage result

        Returns:
            TriageResult

        Raises:
            TriageResultNotFoundError: If result not found
        """
        result = await self.triage_result_repo.get_by_id(triage_id)
        if not result:
            raise TriageResultNotFoundError(str(triage_id))
        return result

    async def get_patient_triage_history(
        self,
        patient_id: UUID,
        limit: int = 10,
    ) -> List[TriageResult]:
        """
        Get triage history for a patient.

        Args:
            patient_id: UUID of the patient
            limit: Maximum number of results (1-100)

        Returns:
            List of TriageResult objects, most recent first

        Raises:
            PatientNotFoundError: If patient doesn't exist
        """
        # Validate limit bounds
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100

        # Verify patient exists
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundError(str(patient_id))

        return await self.triage_result_repo.get_by_patient_id(patient_id, limit)

    async def get_available_specialties(self) -> List[str]:
        """Get list of all available specialties from triage rules."""
        return await self.triage_rule_repo.get_unique_specialties()

    async def link_triage_to_appointment(
        self,
        triage_id: UUID,
        appointment_id: UUID,
    ) -> TriageResult:
        """
        Link a triage result to a created appointment.

        Args:
            triage_id: UUID of the triage result
            appointment_id: UUID of the appointment

        Returns:
            Updated TriageResult

        Raises:
            TriageResultNotFoundError: If triage result not found
        """
        result = await self.triage_result_repo.link_to_appointment(
            triage_id,
            appointment_id,
        )
        if not result:
            raise TriageResultNotFoundError(str(triage_id))
        return result
