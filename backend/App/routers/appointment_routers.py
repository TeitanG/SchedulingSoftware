from fastapi import APIRouter
from App.service import create_appointment
from App.db.schemas import AppointmentCreate, appointment_to_dict
from App.db.client import db_client



router = APIRouter(
    prefix= "/appointments",
    tags=["appointment"]
)


@router.get("/")
async def get_appointment():
    appointments = list(db_client.appointments.find())
    return appointments



@router.post("/")
async def new_appointment(appointment : AppointmentCreate):
    new_appoint =create_appointment(**appointment.model_dump())
    return new_appoint




