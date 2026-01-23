"""Unit tests for Triage Service."""
import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from infrastructure.database.models.triage import TriageRule, TriageResult, UrgencyLevel
from infrastructure.database.schemas.triage import TriageAnalyzeRequest
from infrastructure.ext.base import ICD10Code
from services.triage import (
    TriageService,
    DEFAULT_URGENCY,
    DEFAULT_SPECIALTY,
    MAX_SYMPTOMS_PER_REQUEST,
)
from services.errors import PatientNotFoundError, TriageResultNotFoundError


@pytest.fixture
def mock_triage_rule_repo():
    """Mock TriageRuleRepository."""
    return AsyncMock()


@pytest.fixture
def mock_triage_result_repo():
    """Mock TriageResultRepository."""
    return AsyncMock()


@pytest.fixture
def mock_patient_repo():
    """Mock PatientRepository."""
    return AsyncMock()


@pytest.fixture
def mock_nlm_client():
    """Mock NLM Client."""
    return AsyncMock()


@pytest.fixture
def triage_service(mock_triage_rule_repo, mock_triage_result_repo, mock_patient_repo, mock_nlm_client):
    """Create TriageService with mocked dependencies."""
    return TriageService(
        triage_rule_repo=mock_triage_rule_repo,
        triage_result_repo=mock_triage_result_repo,
        patient_repo=mock_patient_repo,
        nlm_client=mock_nlm_client,
    )


@pytest.fixture
def sample_patient():
    """Sample patient mock."""
    patient = MagicMock()
    patient.id = uuid.uuid4()
    patient.user_id = uuid.uuid4()
    return patient


@pytest.fixture
def sample_triage_rules():
    """Sample triage rules."""
    rules = []
    
    # Emergency rule - chest pain
    rule1 = MagicMock(spec=TriageRule)
    rule1.id = uuid.uuid4()
    rule1.icd10_pattern = "R07%"
    rule1.condition_name = "Chest Pain"
    rule1.urgency_level = UrgencyLevel.HIGH
    rule1.recommended_specialty = "Cardiology"
    rule1.priority = 10
    rule1.is_active = True
    rules.append(rule1)
    
    # Medium rule - headache
    rule2 = MagicMock(spec=TriageRule)
    rule2.id = uuid.uuid4()
    rule2.icd10_pattern = "R51%"
    rule2.condition_name = "Headache"
    rule2.urgency_level = UrgencyLevel.MEDIUM
    rule2.recommended_specialty = "Neurology"
    rule2.priority = 5
    rule2.is_active = True
    rules.append(rule2)
    
    return rules


class TestTriageServiceSymptomParsing:
    """Tests for symptom parsing logic."""

    def test_parse_single_symptom(self, triage_service):
        """Test parsing a single symptom."""
        symptoms = triage_service._parse_symptoms("headache")
        assert symptoms == ["headache"]

    def test_parse_comma_separated_symptoms(self, triage_service):
        """Test parsing comma-separated symptoms."""
        symptoms = triage_service._parse_symptoms("headache, nausea, dizziness")
        assert len(symptoms) == 3
        assert "headache" in symptoms
        assert "nausea" in symptoms
        assert "dizziness" in symptoms

    def test_parse_and_separated_symptoms(self, triage_service):
        """Test parsing 'and' separated symptoms."""
        symptoms = triage_service._parse_symptoms("chest pain and difficulty breathing")
        assert len(symptoms) == 2
        assert "chest pain" in symptoms
        assert "difficulty breathing" in symptoms

    def test_parse_mixed_separators(self, triage_service):
        """Test parsing with mixed separators."""
        symptoms = triage_service._parse_symptoms("headache, nausea and fatigue; dizziness")
        assert len(symptoms) == 4

    def test_parse_filters_short_fragments(self, triage_service):
        """Test that very short fragments are filtered out."""
        symptoms = triage_service._parse_symptoms("headache, a, nausea")
        assert len(symptoms) == 2
        assert "a" not in symptoms

    def test_parse_empty_string(self, triage_service):
        """Test parsing empty string returns empty list."""
        symptoms = triage_service._parse_symptoms("")
        assert symptoms == []

    def test_parse_whitespace_only(self, triage_service):
        """Test parsing whitespace-only string returns empty list."""
        symptoms = triage_service._parse_symptoms("   ")
        assert symptoms == []

    def test_parse_limits_symptom_count(self, triage_service):
        """Test that symptom count is limited to MAX_SYMPTOMS_PER_REQUEST."""
        # Create a string with many symptoms
        many_symptoms = ", ".join([f"symptom{i}" for i in range(50)])
        symptoms = triage_service._parse_symptoms(many_symptoms)
        assert len(symptoms) <= MAX_SYMPTOMS_PER_REQUEST


class TestTriageServiceUrgencyDetermination:
    """Tests for urgency level determination."""

    def test_determine_urgency_no_rules(self, triage_service):
        """Test that no rules returns default values."""
        urgency, specialty = triage_service._determine_urgency([])
        assert urgency == DEFAULT_URGENCY
        assert specialty == DEFAULT_SPECIALTY

    def test_determine_urgency_single_rule(self, triage_service, sample_triage_rules):
        """Test urgency with single matching rule."""
        rules = [sample_triage_rules[0]]  # HIGH urgency rule
        urgency, specialty = triage_service._determine_urgency(rules)
        
        assert urgency == UrgencyLevel.HIGH
        assert specialty == "Cardiology"

    def test_determine_urgency_multiple_rules_takes_highest(self, triage_service, sample_triage_rules):
        """Test that highest urgency is selected from multiple rules."""
        urgency, specialty = triage_service._determine_urgency(sample_triage_rules)
        
        # Should select the HIGH urgency rule (Cardiology)
        assert urgency == UrgencyLevel.HIGH
        assert specialty == "Cardiology"


class TestTriageServiceConfidenceCalculation:
    """Tests for confidence score calculation."""

    def test_confidence_all_matched(self, triage_service):
        """Test confidence when all symptoms are matched."""
        confidence = triage_service._calculate_confidence(
            total_symptoms=3,
            matched_symptoms=3,
            matched_rules=3
        )
        assert confidence == 1.0

    def test_confidence_no_matched(self, triage_service):
        """Test confidence when no symptoms are matched."""
        confidence = triage_service._calculate_confidence(
            total_symptoms=3,
            matched_symptoms=0,
            matched_rules=0
        )
        assert confidence == 0.0

    def test_confidence_partial_match(self, triage_service):
        """Test confidence with partial matching."""
        confidence = triage_service._calculate_confidence(
            total_symptoms=4,
            matched_symptoms=2,
            matched_rules=1
        )
        # 50% symptom match + ~17% rule bonus = ~0.42
        assert 0.0 < confidence < 1.0

    def test_confidence_zero_symptoms(self, triage_service):
        """Test confidence with zero symptoms."""
        confidence = triage_service._calculate_confidence(
            total_symptoms=0,
            matched_symptoms=0,
            matched_rules=0
        )
        assert confidence == 0.0


class TestTriageServiceAnalyzeSymptoms:
    """Tests for the main analyze_symptoms method."""

    @pytest.mark.asyncio
    async def test_analyze_symptoms_patient_not_found(
        self, 
        triage_service, 
        mock_patient_repo
    ):
        """Test that missing patient raises error."""
        mock_patient_repo.get_by_id.return_value = None
        
        request = TriageAnalyzeRequest(
            patient_id=uuid.uuid4(),
            symptoms="headache"
        )
        
        with pytest.raises(PatientNotFoundError):
            await triage_service.analyze_symptoms(request)

    @pytest.mark.asyncio
    async def test_analyze_symptoms_success(
        self,
        triage_service,
        mock_patient_repo,
        mock_nlm_client,
        mock_triage_rule_repo,
        mock_triage_result_repo,
        sample_patient,
        sample_triage_rules,
    ):
        """Test successful symptom analysis flow."""
        # Setup mocks
        mock_patient_repo.get_by_id.return_value = sample_patient
        
        # NLM client returns ICD-10 code for "chest pain"
        mock_nlm_client.validate_symptom.return_value = ICD10Code(
            code="R07.9",
            description="Chest pain, unspecified",
            category="Chest Pain"
        )
        
        # Triage rules return matching rules
        mock_triage_rule_repo.find_matching_rules.return_value = [sample_triage_rules[0]]
        
        # Create mock saved result
        saved_result = MagicMock(spec=TriageResult)
        saved_result.id = uuid.uuid4()
        saved_result.patient_id = sample_patient.id
        saved_result.urgency_level = UrgencyLevel.HIGH
        saved_result.recommended_specialty = "Cardiology"
        saved_result.created_at = datetime.utcnow()
        mock_triage_result_repo.create.return_value = saved_result
        
        # Execute
        request = TriageAnalyzeRequest(
            patient_id=sample_patient.id,
            symptoms="chest pain"
        )
        
        result = await triage_service.analyze_symptoms(request)
        
        # Verify
        assert result.urgency_level == UrgencyLevel.HIGH
        assert result.recommended_specialty == "Cardiology"
        assert len(result.processed_symptoms) == 1
        assert result.processed_symptoms[0].matched is True
        assert result.processed_symptoms[0].icd10_code == "R07.9"

    @pytest.mark.asyncio
    async def test_analyze_symptoms_no_nlm_match(
        self,
        triage_service,
        mock_patient_repo,
        mock_nlm_client,
        mock_triage_rule_repo,
        mock_triage_result_repo,
        sample_patient,
    ):
        """Test analysis when NLM doesn't find matches."""
        mock_patient_repo.get_by_id.return_value = sample_patient
        mock_nlm_client.validate_symptom.return_value = None
        mock_triage_rule_repo.find_matching_rules.return_value = []
        
        saved_result = MagicMock(spec=TriageResult)
        saved_result.id = uuid.uuid4()
        saved_result.patient_id = sample_patient.id
        saved_result.urgency_level = DEFAULT_URGENCY
        saved_result.recommended_specialty = DEFAULT_SPECIALTY
        saved_result.created_at = datetime.utcnow()
        mock_triage_result_repo.create.return_value = saved_result
        
        request = TriageAnalyzeRequest(
            patient_id=sample_patient.id,
            symptoms="some random text"
        )
        
        result = await triage_service.analyze_symptoms(request)
        
        # Should fall back to defaults
        assert result.urgency_level == DEFAULT_URGENCY
        assert result.recommended_specialty == DEFAULT_SPECIALTY
        assert len(result.matched_rules) == 0


class TestTriageServiceHelperMethods:
    """Tests for helper methods."""

    @pytest.mark.asyncio
    async def test_get_available_specialties(
        self,
        triage_service,
        mock_triage_rule_repo,
    ):
        """Test getting available specialties."""
        mock_triage_rule_repo.get_unique_specialties.return_value = [
            "Cardiology",
            "Neurology",
            "General Practice"
        ]

        specialties = await triage_service.get_available_specialties()

        assert len(specialties) == 3
        assert "Cardiology" in specialties

    @pytest.mark.asyncio
    async def test_get_patient_triage_history_not_found(
        self,
        triage_service,
        mock_patient_repo,
    ):
        """Test that getting history for missing patient raises error."""
        mock_patient_repo.get_by_id.return_value = None

        with pytest.raises(PatientNotFoundError):
            await triage_service.get_patient_triage_history(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_patient_triage_history_limit_clamped(
        self,
        triage_service,
        mock_patient_repo,
        mock_triage_result_repo,
        sample_patient,
    ):
        """Test that history limit is clamped to valid bounds."""
        mock_patient_repo.get_by_id.return_value = sample_patient
        mock_triage_result_repo.get_by_patient_id.return_value = []

        # Test with very large limit - should be clamped
        await triage_service.get_patient_triage_history(sample_patient.id, limit=500)
        mock_triage_result_repo.get_by_patient_id.assert_called_with(
            sample_patient.id, 100  # Clamped to max
        )

    @pytest.mark.asyncio
    async def test_link_triage_to_appointment(
        self,
        triage_service,
        mock_triage_result_repo,
    ):
        """Test linking triage result to appointment."""
        triage_id = uuid.uuid4()
        appointment_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.appointment_id = appointment_id
        mock_triage_result_repo.link_to_appointment.return_value = mock_result

        result = await triage_service.link_triage_to_appointment(triage_id, appointment_id)

        mock_triage_result_repo.link_to_appointment.assert_called_once_with(
            triage_id, appointment_id
        )
        assert result.appointment_id == appointment_id

    @pytest.mark.asyncio
    async def test_link_triage_to_appointment_not_found(
        self,
        triage_service,
        mock_triage_result_repo,
    ):
        """Test linking non-existent triage result raises error."""
        mock_triage_result_repo.link_to_appointment.return_value = None

        with pytest.raises(TriageResultNotFoundError):
            await triage_service.link_triage_to_appointment(uuid.uuid4(), uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_triage_result_or_raise_not_found(
        self,
        triage_service,
        mock_triage_result_repo,
    ):
        """Test that get_triage_result_or_raise raises error when not found."""
        mock_triage_result_repo.get_by_id.return_value = None

        with pytest.raises(TriageResultNotFoundError):
            await triage_service.get_triage_result_or_raise(uuid.uuid4())


class TestTriageServiceInitialization:
    """Tests for TriageService initialization."""

    def test_init_with_none_triage_rule_repo_raises_error(
        self,
        mock_triage_result_repo,
        mock_patient_repo,
        mock_nlm_client,
    ):
        """Test that None triage_rule_repo raises ValueError."""
        with pytest.raises(ValueError, match="triage_rule_repo cannot be None"):
            TriageService(
                triage_rule_repo=None,
                triage_result_repo=mock_triage_result_repo,
                patient_repo=mock_patient_repo,
                nlm_client=mock_nlm_client,
            )

    def test_init_with_none_nlm_client_raises_error(
        self,
        mock_triage_rule_repo,
        mock_triage_result_repo,
        mock_patient_repo,
    ):
        """Test that None nlm_client raises ValueError."""
        with pytest.raises(ValueError, match="nlm_client cannot be None"):
            TriageService(
                triage_rule_repo=mock_triage_rule_repo,
                triage_result_repo=mock_triage_result_repo,
                patient_repo=mock_patient_repo,
                nlm_client=None,
            )
