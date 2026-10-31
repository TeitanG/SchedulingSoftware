from fastapi import APIRouter, Depends

from App.db.schemas import AppointmentCreate, AppointmentPatch, PutAppointment
from App.dependencies import get_appointment_repository, get_appointment_services
from App.repositories import AppointmentRepository
from App.service import (
    AppointmentService,
    get_all_appointments,
    search_appointment_by_id,
)

router = APIRouter(prefix="/appointments", tags=["appointment"])


@router.get(
    "/",
)
async def get_appointment(
    appointment_repo: AppointmentRepository = Depends(get_appointment_repository),
):
    appointments = get_all_appointments(appointment_repo)
    return appointments


@router.get("/{id}")
async def get_appointments_by_id(
    id: str,
    appointment_repo: AppointmentRepository = Depends(get_appointment_repository),
):
    appointment = search_appointment_by_id(id, appointment_repo)
    return appointment


@router.post("/")
async def new_appoint(
    appointment: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_repository),
):
    return service.create_appointment(appointment)


@router.delete("/{id}")
async def delete_appointment(
    id: str,
    service: AppointmentService = Depends(get_appointment_repository),
):
    return service.delete_appointments(id)


@router.put("/{id}")
async def update_entire_appointment(
    id: str,
    appointment: PutAppointment,
    service: AppointmentService = Depends(get_appointment_services),
):
    update_appointment_put = service.put_appointment(id, appointment)
    return update_appointment_put


@router.patch("/{id}")
async def update_appointment(
    id: str,
    appointment: AppointmentPatch,
    service: AppointmentService = Depends(get_appointment_repository),
):
    updated_appointment = service.update_appointment_patch(id, appointment)
    return updated_appointment
