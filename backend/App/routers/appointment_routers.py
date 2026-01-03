from fastapi import APIRouter
from App.service import create_appointment, search_appointment_by_id, delete_appointments, update_appointment_patch
from App.db.schemas import AppointmentCreate, appointment_to_dict, PatchUpdateAppointment
from App.db.client import db_client
from bson import ObjectId



router = APIRouter(
    prefix= "/appointments",
    tags=["appointment"]
)


@router.get("/")
async def get_appointment():
    return[appointment_to_dict(appointment) for appointment in db_client.appointments.find()]

@router.get("/{id}")
async def get_appointments_by_id(id: str):
    return search_appointment_by_id("_id", id)


@router.post("/")
async def new_appoint(appointment : AppointmentCreate):
    create_appoint =create_appointment(**appointment.model_dump())
    return create_appoint

@router.delete("/{id}")
async def delete_appointment(id : str):
     return delete_appointments("_id", id)

@router.put("/{id}")
async def update_entire_appointment(id: str, appointment: AppointmentCreate):
    pass
    

@router.patch("/{id}")
async def update_appointment(id: str, appointment: PatchUpdateAppointment):
    updated_appointment = update_appointment_patch(id, appointment)
    return updated_appointment




