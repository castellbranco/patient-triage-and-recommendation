# Clean Architecture in Patient Triage System

## Overview

This project strictly follows **Clean Architecture** principles as defined by Robert C. Martin (Uncle Bob). The architecture ensures maintainability, testability, and independence from frameworks and external systems.

## Core Principles

### 1. Dependency Rule
Dependencies can only point **inward**. Inner layers cannot know anything about outer layers.

```
Presentation (Outermost) ──→ Infrastructure
                             ↓
                        Application
                             ↓
                        Domain (Innermost)
```

### 2. Independence
- **Independent of Frameworks**: Business logic doesn't depend on FastAPI, SQLAlchemy, etc.
- **Independent of UI**: Can swap Streamlit for React without touching business logic
- **Independent of Database**: Can swap PostgreSQL for MongoDB without changing domain
- **Independent of External Services**: NLM API is abstracted behind interfaces
- **Testable**: Business logic can be tested without UI, database, or external services

## Architecture Layers

### Domain Layer (`app/domain/`)

**Purpose**: Core business logic and entities

**Contains**:
- **Entities**: Core business objects (User, Patient, Appointment, TriageResult)
- **Value Objects**: Immutable values (Email, PhoneNumber, ICD10Code, UrgencyLevel)
- **Domain Exceptions**: Business rule violations (InvalidSymptomError, etc.)

**Rules**:
- ❌ No dependencies on other layers
- ❌ No framework dependencies
- ✅ Pure Python business logic
- ✅ Rich domain models with behavior

**Example**:
```python
# domain/entities/patient.py
class Patient:
    def __init__(self, email: Email, phone: PhoneNumber):
        self.email = email
        self.phone = phone
        self.medical_history: List[MedicalRecord] = []

    def add_medical_record(self, record: MedicalRecord) -> None:
        """Business logic for adding medical records"""
        if record.date > datetime.now():
            raise InvalidMedicalRecordError("Future dates not allowed")
        self.medical_history.append(record)
```

### Application Layer (`app/application/`)

**Purpose**: Business logic orchestration (use cases)

**Contains**:
- **Use Cases**: Application-specific business rules (RegisterPatientUseCase, TriageSymptomsUseCase)
- **DTOs**: Data Transfer Objects for request/response
- **Interfaces**: Abstract definitions (IPatientRepository, INLMClient)

**Rules**:
- ✅ Can depend on Domain layer
- ❌ Cannot depend on Infrastructure or Presentation
- ✅ Defines interfaces for infrastructure
- ✅ Contains application-specific business rules

**Example**:
```python
# application/use_cases/register_patient.py
class RegisterPatientUseCase:
    def __init__(self, patient_repo: IPatientRepository):
        self.patient_repo = patient_repo

    async def execute(self, dto: RegisterPatientDTO) -> Patient:
        # Business logic orchestration
        email = Email(dto.email)
        phone = PhoneNumber(dto.phone)
        patient = Patient(email, phone)
        return await self.patient_repo.save(patient)
```

### Infrastructure Layer (`app/infrastructure/`)

**Purpose**: Implementation of external systems

**Contains**:
- **Database**: SQLAlchemy models, connection management
- **Repositories**: Concrete implementations of repository interfaces
- **External Clients**: NLM API adapter, email service, etc.
- **Configuration**: Environment and application settings

**Rules**:
- ✅ Implements interfaces defined in Application layer
- ✅ Can depend on Domain and Application layers
- ✅ Framework-specific code lives here
- ✅ All external dependencies

**Example**:
```python
# infrastructure/repositories/patient_repository.py
class SQLAlchemyPatientRepository(IPatientRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, patient: Patient) -> Patient:
        # Map domain entity to SQLAlchemy model
        db_patient = PatientModel.from_entity(patient)
        self.session.add(db_patient)
        await self.session.commit()
        return patient
```

### Presentation Layer (`app/presentation/`)

**Purpose**: API endpoints and request/response handling

**Contains**:
- **API Routes**: FastAPI routers (`public/v1/`, `internal/`)
- **Dependencies**: FastAPI dependency injection
- **Serialization**: Converting between DTOs and HTTP

**Rules**:
- ✅ Can depend on Application and Domain layers
- ✅ Handles HTTP concerns (validation, status codes, etc.)
- ❌ Contains NO business logic
- ✅ Thin layer that delegates to use cases

**Example**:
```python
# presentation/api/public/v1/patients.py
@router.post("/patients", status_code=201)
async def register_patient(
    dto: RegisterPatientRequest,
    use_case: RegisterPatientUseCase = Depends(get_register_patient_use_case)
):
    patient = await use_case.execute(dto)
    return PatientResponse.from_entity(patient)
```

## Dependency Injection

We use **Dishka** (ADR-002) for dependency injection to maintain clean dependencies:

```python
# Presentation layer depends on Application layer interfaces
async def get_register_patient_use_case(
    container: Container = Depends(get_container)
) -> RegisterPatientUseCase:
    return await container.get(RegisterPatientUseCase)

# Infrastructure provides concrete implementations
def setup_container() -> Container:
    container = Container()
    container.register(IPatientRepository, SQLAlchemyPatientRepository)
    container.register(RegisterPatientUseCase)
    return container
```

## Data Flow

### Request Flow (Inward)
```
HTTP Request
    ↓
Presentation (API Route)
    ↓
Application (Use Case)
    ↓
Domain (Business Logic)
    ↓
Application (Repository Interface)
    ↓
Infrastructure (Repository Implementation)
    ↓
Database
```

### Response Flow (Outward)
```
Database
    ↓
Infrastructure (Repository)
    ↓
Application (Use Case)
    ↓
Domain (Entity)
    ↓
Presentation (DTO/Response)
    ↓
HTTP Response
```

## Benefits

### Testability
- **Unit Tests**: Test domain logic without any dependencies
- **Integration Tests**: Test use cases with mock repositories
- **E2E Tests**: Test full stack with real infrastructure

### Flexibility
- Swap PostgreSQL for MongoDB: Only change Infrastructure layer
- Swap FastAPI for Flask: Only change Presentation layer
- Change NLM API client: Only change Infrastructure layer

### Maintainability
- Clear separation of concerns
- Each layer has a single responsibility
- Easy to navigate and understand

## Common Patterns

### Repository Pattern
Abstract data access behind interfaces:
```python
# Application layer defines interface
class IPatientRepository(Protocol):
    async def save(self, patient: Patient) -> Patient:
        ...
    async def find_by_id(self, id: UUID) -> Optional[Patient]:
        ...

# Infrastructure implements it
class SQLAlchemyPatientRepository(IPatientRepository):
    # Implementation details
```

### Use Case Pattern
Each application feature is a use case:
```python
class TriageSymptomsUseCase:
    def __init__(
        self,
        symptom_repo: ISymptomRepository,
        nlm_client: INLMClient,
        triage_engine: TriageEngine
    ):
        # Dependencies injected

    async def execute(self, dto: TriageRequestDTO) -> TriageResult:
        # Orchestrate business logic
```

### Value Objects
Encapsulate validation in value objects:
```python
class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidEmailError(value)
        self.value = value

    @staticmethod
    def _is_valid(value: str) -> bool:
        # Validation logic
```

## Anti-Patterns to Avoid

❌ **Don't** put business logic in API routes
❌ **Don't** let Domain layer import from Infrastructure
❌ **Don't** create circular dependencies between layers
❌ **Don't** bypass use cases and call repositories directly from routes
❌ **Don't** mix concerns (e.g., database code in use cases)

## References

- [The Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architecture Book](https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
