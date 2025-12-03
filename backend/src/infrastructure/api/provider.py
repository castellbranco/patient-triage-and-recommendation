"""
Provider API Module - Routes for provider endpoints
"""

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from infrastructure.api.utils import Pagination, ProviderServiceDep
from infrastructure.database.schemas.provider import (
    ProviderListResponse,
    ProviderRegister,
    ProviderResponse,
    ProviderUpdate,
)


router = APIRouter(prefix="/providers", tags=["Providers"], route_class=DishkaRoute)


@router.post(
    "/register",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register provider",
    responses={
        201: {"description": "Provider registered successfully"},
        409: {"description": "Email or license already registered"},
    },
)
async def register_provider(
    data: ProviderRegister, service: ProviderServiceDep
) -> ProviderResponse:
    """Register a new provider (creates User + Provider in one call)."""
    provider = await service.register_provider(data)
    return ProviderResponse.model_validate(provider)


@router.get(
    "",
    response_model=ProviderListResponse,
    summary="List providers",
    responses={200: {"description": "Providers retrieved"}},
)
async def list_providers(
    service: ProviderServiceDep,
    pagination: Pagination,
    specialty: str | None = Query(None, description="Filter by specialty"),
    accepting_patients: bool | None = Query(None, description="Filter by accepting new patients"),
) -> ProviderListResponse:
    """List providers with pagination and optional filters."""
    if specialty:
        providers = await service.list_by_specialty(specialty)
        total = len(providers)
        providers = providers[pagination.skip : pagination.skip + pagination.limit]
    elif accepting_patients is True:
        providers = await service.list_accepting_patients()
        total = len(providers)
        providers = providers[pagination.skip : pagination.skip + pagination.limit]
    else:
        providers = await service.list_providers(skip=pagination.skip, limit=pagination.limit)
        total = await service.count_providers()

    return ProviderListResponse(
        providers=[ProviderResponse.model_validate(p) for p in providers],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Get provider",
    responses={
        200: {"description": "Provider retrieved"},
        404: {"description": "Provider not found"},
    },
)
async def get_provider(provider_id: UUID, service: ProviderServiceDep) -> ProviderResponse:
    """Get a provider by ID."""
    provider = await service.get_provider_or_raise(provider_id)
    return ProviderResponse.model_validate(provider)


@router.patch(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Update provider",
    responses={
        200: {"description": "Provider updated"},
        404: {"description": "Provider not found"},
        409: {"description": "License already registered"},
    },
)
async def update_provider(
    provider_id: UUID, data: ProviderUpdate, service: ProviderServiceDep
) -> ProviderResponse:
    """Update a provider's profile. Only provided fields are updated."""
    provider = await service.update_provider(provider_id, data)
    return ProviderResponse.model_validate(provider)


@router.delete(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Delete provider",
    responses={
        200: {"description": "Provider deleted"},
        404: {"description": "Provider not found"},
    },
)
async def delete_provider(provider_id: UUID, service: ProviderServiceDep) -> ProviderResponse:
    """Soft-delete a provider (data retained for audit)."""
    provider = await service.delete_provider(provider_id)
    return ProviderResponse.model_validate(provider)
