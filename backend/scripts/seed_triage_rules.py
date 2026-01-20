"""
Seed script for initial triage rules.

Run with: pdm run python scripts/seed_triage_rules.py
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.database.base import create_database_engine, create_session_factory
from infrastructure.database.models.triage import TriageRule, UrgencyLevel


# Initial triage rules based on common ICD-10 patterns
INITIAL_RULES = [
    # EMERGENCY - Immediate life-threatening conditions
    {
        "icd10_pattern": "I21%",
        "condition_name": "Acute Myocardial Infarction (Heart Attack)",
        "urgency_level": UrgencyLevel.EMERGENCY,
        "recommended_specialty": "Cardiology",
        "description": "Acute heart attack - requires immediate emergency care",
        "priority": 100,
    },
    {
        "icd10_pattern": "I63%",
        "condition_name": "Cerebral Infarction (Stroke)",
        "urgency_level": UrgencyLevel.EMERGENCY,
        "recommended_specialty": "Neurology",
        "description": "Stroke - time-critical emergency",
        "priority": 100,
    },
    {
        "icd10_pattern": "J96%",
        "condition_name": "Respiratory Failure",
        "urgency_level": UrgencyLevel.EMERGENCY,
        "recommended_specialty": "Pulmonology",
        "description": "Acute respiratory failure",
        "priority": 100,
    },
    {
        "icd10_pattern": "T78.2%",
        "condition_name": "Anaphylactic Shock",
        "urgency_level": UrgencyLevel.EMERGENCY,
        "recommended_specialty": "Emergency Medicine",
        "description": "Severe allergic reaction",
        "priority": 100,
    },
    
    # HIGH - Urgent conditions requiring prompt attention
    {
        "icd10_pattern": "R07%",
        "condition_name": "Chest Pain",
        "urgency_level": UrgencyLevel.HIGH,
        "recommended_specialty": "Cardiology",
        "description": "Chest pain - needs evaluation to rule out cardiac causes",
        "priority": 80,
    },
    {
        "icd10_pattern": "J18%",
        "condition_name": "Pneumonia",
        "urgency_level": UrgencyLevel.HIGH,
        "recommended_specialty": "Pulmonology",
        "description": "Lung infection requiring treatment",
        "priority": 75,
    },
    {
        "icd10_pattern": "K35%",
        "condition_name": "Acute Appendicitis",
        "urgency_level": UrgencyLevel.HIGH,
        "recommended_specialty": "General Surgery",
        "description": "Appendicitis - may require surgery",
        "priority": 80,
    },
    {
        "icd10_pattern": "N10%",
        "condition_name": "Acute Pyelonephritis (Kidney Infection)",
        "urgency_level": UrgencyLevel.HIGH,
        "recommended_specialty": "Nephrology",
        "description": "Kidney infection requiring antibiotics",
        "priority": 70,
    },
    {
        "icd10_pattern": "R06.0%",
        "condition_name": "Dyspnea (Difficulty Breathing)",
        "urgency_level": UrgencyLevel.HIGH,
        "recommended_specialty": "Pulmonology",
        "description": "Breathing difficulties",
        "priority": 75,
    },
    
    # MEDIUM - Conditions requiring timely care
    {
        "icd10_pattern": "R51%",
        "condition_name": "Headache",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Neurology",
        "description": "Persistent or severe headache",
        "priority": 50,
    },
    {
        "icd10_pattern": "G43%",
        "condition_name": "Migraine",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Neurology",
        "description": "Migraine headache",
        "priority": 45,
    },
    {
        "icd10_pattern": "M54%",
        "condition_name": "Back Pain",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Orthopedics",
        "description": "Back pain - may need imaging",
        "priority": 40,
    },
    {
        "icd10_pattern": "K21%",
        "condition_name": "Gastroesophageal Reflux Disease (GERD)",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Gastroenterology",
        "description": "Acid reflux symptoms",
        "priority": 35,
    },
    {
        "icd10_pattern": "N39.0%",
        "condition_name": "Urinary Tract Infection",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Urology",
        "description": "UTI - needs antibiotics",
        "priority": 45,
    },
    {
        "icd10_pattern": "J06%",
        "condition_name": "Upper Respiratory Infection",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "General Practice",
        "description": "Upper respiratory symptoms",
        "priority": 30,
    },
    {
        "icd10_pattern": "R11%",
        "condition_name": "Nausea and Vomiting",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "Gastroenterology",
        "description": "Persistent nausea/vomiting",
        "priority": 40,
    },
    
    # LOW - Routine care conditions
    {
        "icd10_pattern": "J00%",
        "condition_name": "Common Cold",
        "urgency_level": UrgencyLevel.LOW,
        "recommended_specialty": "General Practice",
        "description": "Common cold symptoms",
        "priority": 10,
    },
    {
        "icd10_pattern": "H10%",
        "condition_name": "Conjunctivitis (Pink Eye)",
        "urgency_level": UrgencyLevel.LOW,
        "recommended_specialty": "Ophthalmology",
        "description": "Eye infection",
        "priority": 15,
    },
    {
        "icd10_pattern": "L20%",
        "condition_name": "Atopic Dermatitis (Eczema)",
        "urgency_level": UrgencyLevel.LOW,
        "recommended_specialty": "Dermatology",
        "description": "Skin condition - eczema",
        "priority": 10,
    },
    {
        "icd10_pattern": "J30%",
        "condition_name": "Allergic Rhinitis",
        "urgency_level": UrgencyLevel.LOW,
        "recommended_specialty": "Allergy/Immunology",
        "description": "Seasonal allergies",
        "priority": 10,
    },
    {
        "icd10_pattern": "R50%",
        "condition_name": "Fever",
        "urgency_level": UrgencyLevel.MEDIUM,
        "recommended_specialty": "General Practice",
        "description": "Fever - needs evaluation",
        "priority": 40,
    },
]


async def seed_triage_rules():
    """Seed the database with initial triage rules."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/triage_db"
    )
    
    engine = create_database_engine(database_url, echo=True)
    session_factory = create_session_factory(engine)
    
    async with session_factory() as session:
        # Check if rules already exist
        from sqlalchemy import select, func
        count_result = await session.execute(
            select(func.count()).select_from(TriageRule)
        )
        existing_count = count_result.scalar_one()
        
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} triage rules. Skipping seed.")
            print("   To re-seed, delete existing rules first.")
            return
        
        # Insert rules
        print(f"🌱 Seeding {len(INITIAL_RULES)} triage rules...")
        
        for rule_data in INITIAL_RULES:
            rule = TriageRule(**rule_data)
            session.add(rule)
        
        await session.commit()
        
        print(f"✅ Successfully seeded {len(INITIAL_RULES)} triage rules!")
        print("\n📋 Rules by urgency level:")
        
        # Summary
        for level in UrgencyLevel:
            level_rules = [r for r in INITIAL_RULES if r["urgency_level"] == level]
            print(f"   {level.value.upper()}: {len(level_rules)} rules")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_triage_rules())
