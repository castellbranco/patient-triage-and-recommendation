# ADR-005: NLM Medical Conditions API for Symptom Standardization

**Status**: Accepted

**Date**: 2024-01-XX

**Deciders**: Development Team

## Context

The Patient Triage System needs to standardize patient-reported symptoms to:
1. Validate symptom input against medical terminology
2. Map symptoms to ICD-10 codes for clinical accuracy
3. Enable automated triage based on standardized data
4. Support autocomplete for symptom entry
5. Ensure compatibility with healthcare standards

Free-text symptom entry leads to:
- Inconsistent terminology ("headache" vs "cephalgia" vs "head pain")
- Spelling errors and typos
- Difficulty in automated triage
- Poor data quality for analytics

We need an external medical API that provides:
- Official ICD-10 code validation
- Symptom autocomplete
- Free to use
- No authentication required (for POC/demo)
- RESTful API with JSON responses

## Decision

We will integrate with the **NLM (National Library of Medicine) Clinical Tables API** for symptom standardization.

Specifically, we'll use:
- **Endpoint**: `https://clinicaltables.nlm.nih.gov/api/conditions/v3/search`
- **Purpose**: Validate and autocomplete medical conditions/symptoms
- **ICD-10 Support**: Returns ICD-10-CM codes

## Rationale

### Why NLM Clinical Tables API?

1. **Official Source**: National Library of Medicine (NLM)
   - Trusted government resource
   - Clinically validated data
   - Updated regularly

2. **ICD-10-CM Codes**: Returns standard codes
   - ICD-10-CM (Clinical Modification) codes
   - Enables standardization across healthcare systems
   - Billing and insurance compatibility

3. **Free and Open**: No cost or authentication
   - Perfect for POC and demo
   - No API keys required
   - No rate limits (reasonable use)

4. **Autocomplete Support**: Search-as-you-type
   - Returns matches for partial input
   - Ranked by relevance
   - Multiple result formats

5. **RESTful API**: Easy integration
   - Simple HTTP GET requests
   - JSON responses
   - Well-documented

6. **Rich Metadata**: Comprehensive information
   - Condition names
   - ICD-10 codes
   - Alternative names/synonyms

## API Examples

### Search for Conditions
```bash
GET https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?terms=headache

Response:
[
  4,
  [
    "Headache",
    "Tension headache",
    "Migraine headache",
    "Cluster headache"
  ],
  null,
  [
    ["Headache", "R51", "Headache"],
    ["Tension headache", "G44.209", "Tension-type headache, unspecified, not intractable"],
    ["Migraine headache", "G43.909", "Migraine, unspecified, not intractable, without status migrainosus"],
    ["Cluster headache", "G44.009", "Cluster headache syndrome, unspecified, not intractable"]
  ]
]
```

### Autocomplete with Fields
```bash
GET https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?terms=fever&sf=primary_name,icd10_code

Response includes:
- Condition name
- ICD-10 code
- Formatted for autocomplete
```

## Integration Architecture

### Adapter Pattern (Infrastructure Layer)

```python
# infrastructure/external/nlm_client.py
from app.application.interfaces import ISymptomValidator

class NLMClient(ISymptomValidator):
    BASE_URL = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"

    async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
        """Validate symptom and return ICD-10 code if found"""
        results = await self._search(symptom)
        if results:
            return ICD10Code(
                code=results[0]["icd10_code"],
                description=results[0]["name"]
            )
        return None

    async def autocomplete(self, partial: str, limit: int = 10) -> List[SymptomSuggestion]:
        """Get autocomplete suggestions for partial symptom"""
        results = await self._search(partial, limit=limit)
        return [
            SymptomSuggestion(
                name=r["name"],
                icd10_code=r["icd10_code"]
            )
            for r in results
        ]
```

### Use Case Integration

```python
# application/use_cases/triage_symptoms.py
class TriageSymptomsUseCase:
    def __init__(self, nlm_client: ISymptomValidator):
        self.nlm_client = nlm_client

    async def execute(self, symptoms: List[str]) -> TriageResult:
        # Validate and standardize symptoms
        validated = []
        for symptom in symptoms:
            icd10 = await self.nlm_client.validate_symptom(symptom)
            if icd10:
                validated.append(icd10)
            else:
                raise InvalidSymptomError(f"Unknown symptom: {symptom}")

        # Perform triage based on validated symptoms
        return self._calculate_triage(validated)
```

## Consequences

### Positive

✅ **Data Quality**: Standardized medical terminology
✅ **Clinical Accuracy**: Official ICD-10-CM codes
✅ **User Experience**: Autocomplete improves input accuracy
✅ **Free**: No cost for development and demo
✅ **No Auth**: Simplifies integration
✅ **Trusted Source**: NLM is authoritative

### Negative

❌ **External Dependency**: Service availability risk
❌ **No SLA**: No guaranteed uptime
❌ **Network Latency**: External API calls add latency
❌ **Limited Control**: Can't modify or extend data
❌ **Rate Limits**: Potential throttling (though undocumented)

### Neutral

⚖️ **Caching Required**: Should cache results (Phase 5)
⚖️ **Fallback Strategy**: Need offline mode for critical operations
⚖️ **Error Handling**: Network failures must be handled gracefully

## Risk Mitigation

### 1. Caching (Phase 5)
```python
# Cache frequently accessed ICD-10 codes in Redis
@cached(ttl=86400)  # 24 hours
async def get_icd10_code(symptom: str) -> Optional[ICD10Code]:
    return await nlm_client.validate_symptom(symptom)
```

### 2. Retry Logic
```python
# Retry on network errors
@retry(max_attempts=3, backoff=exponential)
async def _search(self, term: str) -> List[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(self.BASE_URL, params={"terms": term})
        response.raise_for_status()
        return self._parse_response(response.json())
```

### 3. Circuit Breaker (Phase 6)
```python
# Prevent cascading failures
@circuit_breaker(failure_threshold=5, recovery_timeout=60)
async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
    # Implementation
```

### 4. Offline Fallback
```python
# Local ICD-10 database for critical symptoms
if not online:
    return await local_icd10_db.search(symptom)
```

## Alternatives Considered

### Custom ICD-10 Database
- ✅ Full control
- ✅ No external dependency
- ❌ Maintenance burden
- ❌ Data updates required
- ❌ No autocomplete out of box
- **Rejected**: Too much overhead for initial phases

### UMLS API (Unified Medical Language System)
- ✅ Comprehensive medical ontology
- ✅ Multiple code systems
- ❌ Requires authentication
- ❌ API key management
- ❌ More complex
- **Rejected**: Overkill for our use case

### SNOMED CT API
- ✅ Detailed clinical terminology
- ✅ International standard
- ❌ Licensing required
- ❌ Complex hierarchy
- ❌ Steep learning curve
- **Rejected**: Licensing complexity

### OpenMRS Concept Dictionary
- ✅ Open source
- ✅ Healthcare-focused
- ❌ Requires self-hosting
- ❌ Additional infrastructure
- ❌ Maintenance overhead
- **Rejected**: Adds infrastructure complexity

## Implementation Phases

### Phase 2 (v0.2.0-triage-core)
- ✅ Basic NLM client implementation
- ✅ Symptom validation in use cases
- ✅ Error handling for API failures

### Phase 3 (v0.3.0-security)
- ✅ Audit logging of validated symptoms
- ✅ Rate limiting on frontend to prevent abuse

### Phase 5 (v0.5.0-scale)
- ✅ Redis caching of ICD-10 lookups
- ✅ Metrics on cache hit rate

### Phase 6 (v0.6.0-production)
- ✅ Circuit breaker pattern
- ✅ Monitoring and alerting on API failures
- ✅ Offline fallback mechanism

## Testing Strategy

### Unit Tests
```python
# Mock NLM client for unit tests
class MockNLMClient(ISymptomValidator):
    async def validate_symptom(self, symptom: str) -> Optional[ICD10Code]:
        if symptom.lower() == "headache":
            return ICD10Code(code="R51", description="Headache")
        return None
```

### Integration Tests
```python
# Test against real NLM API (in CI/CD)
@pytest.mark.integration
async def test_nlm_client_real_api():
    client = NLMClient()
    result = await client.validate_symptom("headache")
    assert result is not None
    assert result.code == "R51"
```

### Contract Tests
```python
# Ensure API response format hasn't changed
@pytest.mark.contract
async def test_nlm_api_response_format():
    # Validate response structure
```

## Monitoring

### Metrics to Track
- API response time (P50, P95, P99)
- Error rate (network, validation, parsing)
- Cache hit rate (Phase 5)
- Most searched symptoms

### Alerts
- API unavailable for > 5 minutes
- Error rate > 10%
- Response time > 2 seconds

## Review Date

- **Phase 2**: After initial implementation
- **Phase 5**: After caching implementation
- **Phase 6**: Before production deployment
- **Annually**: Review for alternatives or improvements

## References

- [NLM Clinical Tables Documentation](https://clinicaltables.nlm.nih.gov/)
- [ICD-10-CM Official Guidelines](https://www.cdc.gov/nchs/icd/icd-10-cm.htm)
- [UMLS (alternative)](https://www.nlm.nih.gov/research/umls/)

## Notes

- Phase 2 focuses on integration with triage logic
- Phase 5 adds performance optimization via caching
- Consider UMLS API for future enhancements if more comprehensive data needed
- Offline fallback critical for production healthcare system
