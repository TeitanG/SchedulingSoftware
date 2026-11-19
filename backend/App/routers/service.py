import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.service import Service, ServiceCreate, ServicePublic, ServiceUpdate
from App.dependencies.dependencies import ServiceServiceDep

router = APIRouter(prefix="/business/{business_id}/services", tags=["Service"])


@router.post("/", response_model=ServicePublic, status_code=status.HTTP_201_CREATED)
def create_service(
    business_id: uuid.UUID, data: ServiceCreate, services: ServiceServiceDep
) -> Service:
    return services.create(business_id, data)


@router.get("/", response_model=list[ServicePublic])
def list_services(
    services: ServiceServiceDep,
    business_id: uuid.UUID,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Service]:
    return services.list_by_business(
        business_id=business_id, active=active, limit=limit, offset=offset
    )


@router.get("/{service_id}", response_model=ServicePublic)
def get_service(
    business_id: uuid.UUID, service_id: uuid.UUID, services: ServiceServiceDep
) -> Service:
    return services.get(business_id, service_id)


@router.patch("/{service_id}", response_model=ServicePublic)
def patch_service(
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    services: ServiceServiceDep,
    data: ServiceUpdate,
) -> Service:
    return services.update(business_id, service_id, data)
