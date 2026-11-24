import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from App.db.models.appointment_status_history import (
    AppointmentStatusHistory,
    AppointmentStatusHistoryPublic,
)
from App.dependencies.dependencies import AppointmentStatusHistoryServiceDep

router = APIRouter(
    prefix="/business/{business_id}/appointments/{appointment_id}/history",
    tags=["Appointment_Status_History"],
)


@router.get("/", response_model=list[AppointmentStatusHistoryPublic])
def list_by_appointments(
    service: AppointmentStatusHistoryServiceDep,
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AppointmentStatusHistory]:
    return service.list_by_appointment(
        business_id=business_id,
        appointment_id=appointment_id,
        offset=offset,
        limit=limit,
    )
