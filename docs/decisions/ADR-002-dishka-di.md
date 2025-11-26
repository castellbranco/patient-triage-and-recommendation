# ADR-002: Dishka for Dependency Injection

**Status**: Accepted

**Date**: 2024-01-XX

**Deciders**: Development Team

## Context

Our FastAPI backend follows Clean Architecture with clear separation between layers. We need a dependency injection (DI) framework to:

1. Manage dependencies between layers (Application → Infrastructure)
2. Keep presentation layer thin by injecting use cases
3. Enable testability by swapping implementations
4. Handle scoped lifetimes (request-scoped, singleton, etc.)
5. Maintain type safety and IDE support

FastAPI provides basic DI via `Depends()`, but we need more sophisticated features for Clean Architecture:
- Container management
- Lifecycle scopes (request, session, application)
- Framework-agnostic DI (can be used outside FastAPI)
- Type-safe dependency resolution

## Decision

We will use **Dishka** as our dependency injection framework.

## Rationale

### Why Dishka?

1. **Framework Agnostic**: Not tied to FastAPI
   - Can use in background tasks
   - Can use in CLI scripts
   - Can migrate to different frameworks

2. **Type Safe**: Full type checking support
   - MyPy compatible
   - IDE autocomplete works
   - Compile-time error detection

3. **Async First**: Built for async Python
   - Async factories and providers
   - Async context managers
   - No blocking operations

4. **Scopes**: Flexible lifecycle management
   - `APP`: Application lifetime (singletons)
   - `REQUEST`: Per-request instances
   - `SESSION`: Custom scopes
   - Automatic cleanup

5. **Clean Architecture Support**: Designed for it
   - Protocol/interface support
   - Abstract dependencies
   - Implementation swapping

6. **Performance**: Minimal overhead
   - Fast dependency resolution
   - Compiled dependency graph
   - No runtime reflection

## Example Usage

### Define Providers

```python
# infrastructure/di/providers.py
from dishka import Provider, Scope, provide

class InfrastructureProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncEngine:
        engine = create_async_engine(DATABASE_URL)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def get_session(self, engine: AsyncEngine) -> AsyncSession:
        async with AsyncSession(engine) as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_patient_repository(
        self,
        session: AsyncSession
    ) -> IPatientRepository:
        return SQLAlchemyPatientRepository(session)


class ApplicationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_register_patient_use_case(
        self,
        repo: IPatientRepository
    ) -> RegisterPatientUseCase:
        return RegisterPatientUseCase(repo)
```

### Setup Container

```python
# main.py
from dishka import make_container
from dishka.integrations.fastapi import setup_dishka

container = make_container(
    InfrastructureProvider(),
    ApplicationProvider(),
)

setup_dishka(container, app)
```

### Use in Routes

```python
# presentation/api/public/v1/patients.py
from dishka.integrations.fastapi import FromDishka

@router.post("/patients")
async def register_patient(
    dto: RegisterPatientRequest,
    use_case: FromDishka[RegisterPatientUseCase],
):
    patient = await use_case.execute(dto)
    return PatientResponse.from_entity(patient)
```

## Consequences

### Positive

✅ **Testability**: Easy to mock dependencies
✅ **Type Safety**: Full IDE and MyPy support
✅ **Clean Architecture**: Enforces layer separation
✅ **Flexibility**: Swap implementations easily
✅ **Scoping**: Automatic lifecycle management
✅ **Performance**: Minimal overhead
✅ **Framework Independent**: Not locked to FastAPI

### Negative

❌ **Learning Curve**: Developers need to learn Dishka API
❌ **Abstraction**: More indirect than direct instantiation
❌ **Debugging**: Stack traces can be deeper
❌ **Documentation**: Smaller community than alternatives

### Neutral

⚖️ **Boilerplate**: Some setup code required (providers, container)
⚖️ **Testing Setup**: Need to configure container for tests

## Alternatives Considered

### FastAPI Depends Only
- ✅ Built-in, no additional dependency
- ✅ Simple and straightforward
- ❌ Tightly coupled to FastAPI
- ❌ No scoping beyond request
- ❌ Limited container management
- **Rejected**: Insufficient for Clean Architecture needs

### Dependency Injector
- ✅ Mature library
- ✅ Good documentation
- ❌ Synchronous-first design
- ❌ Less type-safe
- ❌ More boilerplate for async
- **Rejected**: Not async-native

### Manual Dependency Injection
- ✅ No framework dependency
- ✅ Maximum control
- ❌ Lots of boilerplate
- ❌ Error-prone
- ❌ Difficult to test
- **Rejected**: Too much manual work

### Lagom
- ✅ Type-safe
- ✅ Container-based
- ❌ Less active development
- ❌ Smaller ecosystem
- ❌ Less FastAPI integration
- **Rejected**: Dishka has better FastAPI support

## Implementation Strategy

### Phase 1: Basic Setup
```python
# Setup basic container with database dependencies
- Engine provider
- Session provider
- Repository providers
```

### Phase 2: Use Cases
```python
# Add application layer providers
- Use case providers
- Service providers
```

### Phase 3: External Services
```python
# Add infrastructure providers
- NLM API client
- Email service
- File storage
```

### Testing
```python
# Test setup with overrides
test_container = make_container(
    InfrastructureProvider(),
    ApplicationProvider(),
    TestProvider(),  # Mock implementations
)
```

## Best Practices

1. **One Provider per Layer**
   - `InfrastructureProvider` for database, external services
   - `ApplicationProvider` for use cases
   - Clear separation of concerns

2. **Use Protocols for Interfaces**
   ```python
   class IPatientRepository(Protocol):
       async def save(self, patient: Patient) -> Patient: ...
   ```

3. **Scope Appropriately**
   - `APP`: Database engine, configuration
   - `REQUEST`: Sessions, repositories, use cases
   - Avoid memory leaks

4. **Type Hints Are Mandatory**
   - Dishka relies on type hints
   - Enable MyPy strict mode

5. **Test with Mock Implementations**
   ```python
   class MockPatientRepository(IPatientRepository):
       # In-memory implementation for tests
   ```

## Review Date

- **Phase 1**: Initial implementation
- **Phase 3**: After adding external services
- **Phase 6**: Before production deployment

## References

- [Dishka Documentation](https://dishka.readthedocs.io/)
- [Dishka GitHub](https://github.com/reagento/dishka)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Clean Architecture DI Patterns](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## Notes

- Dishka integrates seamlessly with FastAPI via `FromDishka`
- Async context managers work perfectly for database sessions
- Can use Dishka outside FastAPI (background tasks, scripts)
- Type safety catches many errors at development time
