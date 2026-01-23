"""
Triage Repository Module

Handles database operations for TriageRule and TriageResult entities.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.triage import (
    TriageRule,
    TriageResult,
    UrgencyLevel,
)
from infrastructure.repo.base import BaseRepository


class TriageRuleRepository(BaseRepository):
    """Repository for TriageRule operations."""
    
    model = TriageRule
    
    async def get_by_id(self, entity_id: UUID) -> Optional[TriageRule]:
        """Get triage rule by ID (no soft delete on this model)."""
        stmt = select(TriageRule).where(TriageRule.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TriageRule]:
        """Get all triage rules with pagination."""
        stmt = (
            select(TriageRule)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_active_rules(self) -> List[TriageRule]:
        """Get all active triage rules ordered by priority."""
        stmt = (
            select(TriageRule)
            .where(TriageRule.is_active == True)  # noqa: E712
            .order_by(TriageRule.priority.desc(), TriageRule.urgency_level.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def find_matching_rules(self, icd10_codes: List[str]) -> List[TriageRule]:
        """
        Find all active rules that match any of the given ICD-10 codes.
        
        Uses SQL LIKE pattern matching against the icd10_pattern field.
        
        Args:
            icd10_codes: List of ICD-10 codes to match (e.g., ["R07.9", "R51"])
            
        Returns:
            List of matching TriageRule entities
        """
        if not icd10_codes:
            return []
        
        # Get all active rules
        active_rules = await self.get_active_rules()
        
        # Match codes against patterns in Python
        # (More flexible than complex SQL LIKE conditions)
        matching_rules = []
        for rule in active_rules:
            pattern = rule.icd10_pattern.replace("%", "")  # Remove SQL wildcards
            for code in icd10_codes:
                # Check if code starts with the pattern (R07% matches R07.9)
                if code.upper().startswith(pattern.upper()):
                    matching_rules.append(rule)
                    break  # Don't add same rule twice
        
        # Sort by priority and urgency level
        urgency_order = {
            UrgencyLevel.EMERGENCY: 4,
            UrgencyLevel.HIGH: 3,
            UrgencyLevel.MEDIUM: 2,
            UrgencyLevel.LOW: 1,
        }
        
        matching_rules.sort(
            key=lambda r: (r.priority, urgency_order.get(r.urgency_level, 0)),
            reverse=True,
        )
        
        return matching_rules
    
    async def get_by_specialty(self, specialty: str) -> List[TriageRule]:
        """Get all active rules for a specific specialty."""
        stmt = (
            select(TriageRule)
            .where(
                and_(
                    TriageRule.is_active == True,  # noqa: E712
                    TriageRule.recommended_specialty.ilike(f"%{specialty}%"),
                )
            )
            .order_by(TriageRule.priority.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_unique_specialties(self) -> List[str]:
        """Get list of unique specialties from active rules."""
        stmt = (
            select(TriageRule.recommended_specialty)
            .where(TriageRule.is_active == True)  # noqa: E712
            .distinct()
            .order_by(TriageRule.recommended_specialty)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]


class TriageResultRepository(BaseRepository):
    """Repository for TriageResult operations."""
    
    model = TriageResult
    
    async def get_by_id(self, entity_id: UUID) -> Optional[TriageResult]:
        """Get triage result by ID (no soft delete on this model)."""
        stmt = select(TriageResult).where(TriageResult.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TriageResult]:
        """Get all triage results with pagination."""
        stmt = (
            select(TriageResult)
            .order_by(TriageResult.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_patient_id(
        self, 
        patient_id: UUID, 
        limit: int = 10
    ) -> List[TriageResult]:
        """Get recent triage results for a patient."""
        stmt = (
            select(TriageResult)
            .where(TriageResult.patient_id == patient_id)
            .order_by(TriageResult.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_urgency(
        self, 
        urgency_level: UrgencyLevel, 
        limit: int = 50
    ) -> List[TriageResult]:
        """Get recent triage results by urgency level."""
        stmt = (
            select(TriageResult)
            .where(TriageResult.urgency_level == urgency_level)
            .order_by(TriageResult.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def link_to_appointment(
        self, 
        triage_result_id: UUID, 
        appointment_id: UUID
    ) -> Optional[TriageResult]:
        """Link a triage result to an appointment."""
        triage_result = await self.get_by_id(triage_result_id)
        if triage_result:
            triage_result.appointment_id = appointment_id
            await self.session.flush()
            await self.session.refresh(triage_result)
        return triage_result
