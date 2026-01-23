"""
Triage Repository Module

Handles database operations for TriageRule and TriageResult entities.
"""

import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.triage import (
    TriageRule,
    TriageResult,
    UrgencyLevel,
)
from infrastructure.repo.base import BaseRepository

# Urgency level ordering for sorting (higher = more urgent)
URGENCY_ORDER = {
    UrgencyLevel.EMERGENCY: 4,
    UrgencyLevel.HIGH: 3,
    UrgencyLevel.MEDIUM: 2,
    UrgencyLevel.LOW: 1,
}


class TriageRuleRepository(BaseRepository):
    """Repository for TriageRule operations."""

    model = TriageRule

    async def get_by_id(self, entity_id: UUID) -> Optional[TriageRule]:
        """Get triage rule by ID (no soft delete on this model)."""
        stmt = select(TriageRule).where(TriageRule.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TriageRule]:
        """
        Get all triage rules with pagination.

        Args:
            skip: Number of records to skip (default 0)
            limit: Maximum records to return (default 100, max 500)

        Returns:
            List of TriageRule entities
        """
        # Validate bounds
        skip = max(0, skip)
        limit = max(1, min(limit, 500))

        stmt = (
            select(TriageRule)
            .order_by(TriageRule.priority.desc(), TriageRule.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_rules(self) -> List[TriageRule]:
        """Get all active triage rules ordered by priority."""
        stmt = (
            select(TriageRule)
            .where(TriageRule.is_active.is_(True))
            .order_by(TriageRule.priority.desc(), TriageRule.urgency_level.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_matching_rules(self, icd10_codes: List[str]) -> List[TriageRule]:
        """
        Find all active rules that match any of the given ICD-10 codes.

        Uses pattern matching against the icd10_pattern field.
        Pattern format: "R07%" matches codes starting with "R07".

        Args:
            icd10_codes: List of ICD-10 codes to match (e.g., ["R07.9", "R51"])

        Returns:
            List of matching TriageRule entities, sorted by priority and urgency
        """
        if not icd10_codes:
            return []

        # Normalize and validate input codes
        normalized_codes = []
        for code in icd10_codes:
            if code and isinstance(code, str):
                normalized = code.strip().upper()
                if normalized:
                    normalized_codes.append(normalized)

        if not normalized_codes:
            return []

        # Get all active rules
        active_rules = await self.get_active_rules()

        # Match codes against patterns in Python
        # This is safer than building dynamic SQL and allows for more flexible matching
        matching_rules: List[TriageRule] = []
        seen_rule_ids = set()

        for rule in active_rules:
            if rule.id in seen_rule_ids:
                continue

            # Convert SQL pattern to prefix match
            # "R07%" -> matches codes starting with "R07"
            pattern = rule.icd10_pattern.replace("%", "").upper()

            for code in normalized_codes:
                if code.startswith(pattern):
                    matching_rules.append(rule)
                    seen_rule_ids.add(rule.id)
                    break  # Don't add same rule twice

        # Sort by priority and urgency level (highest first)
        matching_rules.sort(
            key=lambda r: (r.priority, URGENCY_ORDER.get(r.urgency_level, 0)),
            reverse=True,
        )

        return matching_rules

    async def get_by_specialty(self, specialty: str) -> List[TriageRule]:
        """
        Get all active rules for a specific specialty.

        Args:
            specialty: Specialty name to search for (case-insensitive)

        Returns:
            List of matching TriageRule entities
        """
        if not specialty or not specialty.strip():
            return []

        # Sanitize input - escape SQL LIKE special characters
        sanitized = specialty.strip()
        # Escape % and _ which are SQL LIKE wildcards
        sanitized = sanitized.replace("\\", "\\\\")
        sanitized = sanitized.replace("%", "\\%")
        sanitized = sanitized.replace("_", "\\_")

        stmt = (
            select(TriageRule)
            .where(
                and_(
                    TriageRule.is_active.is_(True),
                    TriageRule.recommended_specialty.ilike(f"%{sanitized}%"),
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
            .where(TriageRule.is_active.is_(True))
            .distinct()
            .order_by(TriageRule.recommended_specialty)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]


class TriageResultRepository(BaseRepository):
    """Repository for TriageResult operations."""

    model = TriageResult

    async def get_by_id(self, entity_id: UUID) -> Optional[TriageResult]:
        """Get triage result by ID (no soft delete on this model)."""
        stmt = select(TriageResult).where(TriageResult.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TriageResult]:
        """
        Get all triage results with pagination.

        Args:
            skip: Number of records to skip (default 0)
            limit: Maximum records to return (default 100, max 500)

        Returns:
            List of TriageResult entities, most recent first
        """
        # Validate bounds
        skip = max(0, skip)
        limit = max(1, min(limit, 500))

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
        limit: int = 10,
    ) -> List[TriageResult]:
        """
        Get recent triage results for a patient.

        Args:
            patient_id: UUID of the patient
            limit: Maximum records to return (default 10, max 100)

        Returns:
            List of TriageResult entities, most recent first
        """
        # Validate limit bounds
        limit = max(1, min(limit, 100))

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
        limit: int = 50,
    ) -> List[TriageResult]:
        """
        Get recent triage results by urgency level.

        Args:
            urgency_level: UrgencyLevel to filter by
            limit: Maximum records to return (default 50, max 200)

        Returns:
            List of TriageResult entities, most recent first
        """
        # Validate limit bounds
        limit = max(1, min(limit, 200))

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
        appointment_id: UUID,
    ) -> Optional[TriageResult]:
        """
        Link a triage result to an appointment.

        Args:
            triage_result_id: UUID of the triage result
            appointment_id: UUID of the appointment

        Returns:
            Updated TriageResult if found, None otherwise
        """
        triage_result = await self.get_by_id(triage_result_id)
        if triage_result is not None:
            triage_result.appointment_id = appointment_id
            await self.session.flush()
            await self.session.refresh(triage_result)
        return triage_result
