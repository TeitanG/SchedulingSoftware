from fastapi import APIRouter
from App.service import create_appointment
from App.db.schemas import AppointmentCreate
from App.db.client import db_client



router = APIRouter(
    prefix= "/appointments",
    tags=["appointment"]
)


@router.get("/")
async def get_appointment():
    appointments = list(db_client.appointments.find())
    return appointments

@router.get("/{id}")
async def get_appointments_by_id(id: str):
    pass


@router.post("/")
async def new_appointment(appointment : AppointmentCreate):
    new_appoint =create_appointment(**appointment.model_dump())
    return new_appoint

@router.put("/{id}")
async def update_entire_appointment():
    pass

@router.patch("/{id}")
async def update_appointment():
    pass

@router.delete("/{id}")
async def delete_appointment():
    pass


