"""
Dishka Dependency Injection Container
"""

import os
from typing import AsyncIterable

from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from infrastructure.database.base import create_database_engine, create_session_factory

# Repositories
from infrastructure.repo.user import UserRepository
from infrastructure.repo.patient import PatientRepository
from infrastructure.repo.provider import ProviderRepository
from infrastructure.repo.appointment import AppointmentRepository

# Services
from services.user import UserService
from services.patient import PatientService
from services.provider import ProviderService
from services.appointment import AppointmentService
from services.auth import AuthService


class InfrastructureProvider(Provider):
    """
    Provider for infrastructure dependencies.
    """

    @provide(scope=Scope.APP)
    def get_database_url(self) -> str:
        """Get database URL from environment."""
        return os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/triage_db"
        )

    @provide(scope=Scope.APP)
    def get_engine(self, database_url: str) -> AsyncEngine:
        """
        Create database engine (singleton).
        """
        echo = os.getenv("SQL_ECHO", "false").lower() == "true"
        return create_database_engine(database_url, echo=echo)

    @provide(scope=Scope.APP)
    def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """
        Create session factory (singleton).
        """
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """
        Create async session (per-request).
        """
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Create UserRepository with injected session."""
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_patient_repository(self, session: AsyncSession) -> PatientRepository:
        """Create PatientRepository with injected session."""
        return PatientRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_provider_repository(self, session: AsyncSession) -> ProviderRepository:
        """Create ProviderRepository with injected session."""
        return ProviderRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_appointment_repository(self, session: AsyncSession) -> AppointmentRepository:
        """Create AppointmentRepository with injected session."""
        return AppointmentRepository(session)


class ServiceProvider(Provider):
    """
    Provider for service layer dependencies.
    """

    @provide(scope=Scope.REQUEST)
    def get_user_service(self, repository: UserRepository) -> UserService:
        """Create UserService with injected repository."""
        return UserService(repository)

    @provide(scope=Scope.REQUEST)
    def get_patient_service(
        self,
        repository: PatientRepository,
        user_service: UserService,
    ) -> PatientService:
        """Create PatientService with injected dependencies."""
        return PatientService(repository, user_service)

    @provide(scope=Scope.REQUEST)
    def get_provider_service(
        self,
        repository: ProviderRepository,
        user_service: UserService,
    ) -> ProviderService:
        """Create ProviderService with injected dependencies."""
        return ProviderService(repository, user_service)

    @provide(scope=Scope.REQUEST)
    def get_appointment_service(
        self,
        repository: AppointmentRepository,
        patient_repository: PatientRepository,
        provider_repository: ProviderRepository,
    ) -> AppointmentService:
        """Create AppointmentService with injected dependencies."""
        return AppointmentService(
            repository,
            patient_repository,
            provider_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, user_service: UserService) -> AuthService:
        """Create AuthService with injected UserService."""
        return AuthService(user_service)


def create_container():
    """
    Create and configure the Dishka DI container.
    """
    return make_async_container(
        InfrastructureProvider(),
        ServiceProvider(),
    )
