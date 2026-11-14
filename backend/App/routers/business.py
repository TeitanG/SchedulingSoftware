import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.business import (
    Business,
    BusinessCreate,
    BusinessPublic,
    BusinessUpdate,
)
from App.dependencies.dependencies import BusinessServiceDep

router = APIRouter(prefix="/business", tags=["business"])


@router.post("/", response_model=BusinessPublic, status_code=status.HTTP_201_CREATED)
def create_business(data: BusinessCreate, service: BusinessServiceDep) -> Business:
    return service.create(data)


@router.get("/", response_model=list[BusinessPublic])
def list_businesses(
    service: BusinessServiceDep,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Business]:
    return service.list_all(active=active, limit=limit, offset=offset)


@router.get("/{business_id}", response_model=BusinessPublic)
def get_business(business_id: uuid.UUID, service: BusinessServiceDep) -> Business:
    return service.get(business_id)


@router.patch("/{business_id}", response_model=BusinessPublic)
def update_business(
    business_id: uuid.UUID, data: BusinessUpdate, service: BusinessServiceDep
) -> Business:
    return service.update(business_id, data)
