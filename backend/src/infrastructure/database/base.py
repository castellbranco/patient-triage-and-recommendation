"""
DataBase Configuration
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""

    pass


class UUIDMixin:
    """UUID Mixin for models"""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )


class TimestampMixin:
    """Timestamp Mixin for models"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        server_default=None,
    )


class SoftDeleteMixin:
    """Soft Delete Mixin for models"""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


def create_database_engine(database_url: str, echo: bool = False):
    """
    Create async SQLAlchemy engine for PostgreSQL.

    Args:
        database_url: PostgreSQL connection string (postgresql+asyncpg://...)
        echo: If True, log all SQL statements (useful for debugging)

    Returns:
        AsyncEngine instance

    Example:
        engine = create_database_engine(
            "postgresql+asyncpg://user:pass@localhost:5432/db",
            echo=True  # Enable in development
        )
    """
    return create_async_engine(
        database_url,
        echo=echo,
        future=True,
        pool_pre_ping=True,  # Verify connections before using
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory.

    Args:
        engine: AsyncEngine from create_database_engine()

    Returns:
        async_sessionmaker that creates AsyncSession instances

    Usage:
        async with session_factory() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Allow access to objects after commit
        autoflush=False,  # Manual control over flushing
        autocommit=False,
    )
