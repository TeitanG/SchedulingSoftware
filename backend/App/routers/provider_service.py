import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.provider_service import (
    ProviderService,
    ProviderServiceCreate,
    ProviderServicePublic,
)
from App.dependencies.dependencies import ProviderServiceDep

router = APIRouter(
    prefix="/business/{business_id}/services/{service_id}/providers",
    tags=["Provider_service"],
)


@router.post(
    "/", response_model=ProviderServicePublic, status_code=status.HTTP_201_CREATED
)
def create_provider(
    providers: ProviderServiceDep,
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    data: ProviderServiceCreate,
) -> ProviderService:
    return providers.add_provider(business_id, service_id, data)


@router.get("/", response_model=list[ProviderServicePublic])
def get_provider(
    providers: ProviderServiceDep,
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ProviderService]:
    return providers.list_providers(business_id, service_id, limit=limit, offset=offset)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_provider(
    providers: ProviderServiceDep,
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    member_id: uuid.UUID,
) -> None:
    providers.remove_provider(business_id, service_id, member_id)
