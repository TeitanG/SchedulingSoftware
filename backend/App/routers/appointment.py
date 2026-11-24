import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentNotesUpdate,
    AppointmentPublic,
    AppointmentStatusUpdate,
)
from App.db.models.common import AppointmentStatus
from App.dependencies.dependencies import AppointmentServiceDep

router = APIRouter(prefix="/business/{business_id}/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
def create_appointment(
    service: AppointmentServiceDep, business_id: uuid.UUID, data: AppointmentCreate
) -> Appointment:
    return service.create(business_id, data)


@router.get("/{appointment_id}", response_model=AppointmentPublic)
def get_appointment(
    service: AppointmentServiceDep, business_id: uuid.UUID, appointment_id: uuid.UUID
) -> Appointment:
    return service.get(business_id=business_id, appointment_id=appointment_id)


@router.get("/", response_model=list[AppointmentPublic])
def list_appointment(
    service: AppointmentServiceDep,
    business_id: uuid.UUID,
    appointment_status: AppointmentStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Appointment]:
    return service.list_by_business(
        business_id, appointment_status=appointment_status, limit=limit, offset=offset
    )


@router.patch("/{appointment_id}/notes", response_model=AppointmentPublic)
def patch_appointment_notes(
    service: AppointmentServiceDep,
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    data: AppointmentNotesUpdate,
) -> Appointment:
    return service.update_notes(
        business_id=business_id, appointment_id=appointment_id, data=data
    )


@router.patch("/{appointment_id}/status", response_model=AppointmentPublic)
def patch_appointment_status(
    service: AppointmentServiceDep,
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    data: AppointmentStatusUpdate,
) -> Appointment:
    return service.update_status(
        business_id=business_id, appointment_id=appointment_id, data=data
    )
