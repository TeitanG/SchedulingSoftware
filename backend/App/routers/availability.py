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
    availability: AvailabilityServiceDep,
    business_id: uuid.UUID,
    members_id: uuid.UUID,
    data: AvailabilityCreate,
) -> Availability:
    return availability.create(business_id, members_id, data)


@router.get("/{availability_id}", response_model=AvailabilityPublic)
def get_availability(
    availability: AvailabilityServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    availability_id: uuid.UUID,
) -> Availability:
    return availability.get(business_id, member_id, availability_id)


@router.get("/", response_model=list[AvailabilityPublic])
def list_availabilities(
    availability: AvailabilityServiceDep,
    member_id: uuid.UUID,
    business_id: uuid.UUID,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Availability]:
    return availability.list_by_member(
        member_id, business_id, active=active, limit=limit, offset=offset
    )


@router.patch("/", response_model=AvailabilityPublic)
def update_availability(
    availability: AvailabilityServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    availability_id: uuid.UUID,
    data: AvailabilityUpdate,
):
    return availability.update(business_id, member_id, availability_id, data)
