import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.availability import (
    Availability,
    AvailabilityCreate,
    AvailabilityPublic,
    AvailabilityUpdate,
)
from App.dependencies.dependencies import AvailabilityServiceDep

router = APIRouter(
    prefix="/business/{business_id}/members/{member_id}/availabilities",
    tags=["Availabilities"],
)


@router.post(
    "/", response_model=AvailabilityPublic, status_code=status.HTTP_201_CREATED
)
def create_availability(
    Service: AvailabilityServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    data: AvailabilityCreate,
) -> Availability:
    return Service.create(business_id, member_id, data)


@router.get("/{availability_id}", response_model=AvailabilityPublic)
def get_availability(
    service: AvailabilityServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    availability_id: uuid.UUID,
) -> Availability:
    return service.get(business_id, member_id, availability_id)


@router.get("/", response_model=list[AvailabilityPublic])
def list_availabilities(
    service: AvailabilityServiceDep,
    member_id: uuid.UUID,
    business_id: uuid.UUID,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Availability]:
    return service.list_by_member(
        member_id, business_id, active=active, limit=limit, offset=offset
    )


@router.patch("/{availability_id}", response_model=AvailabilityPublic)
def update_availability(
    service: AvailabilityServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    availability_id: uuid.UUID,
    data: AvailabilityUpdate,
):
    return service.update(business_id, member_id, availability_id, data)
