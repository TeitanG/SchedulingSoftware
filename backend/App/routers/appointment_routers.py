from fastapi import APIRouter
from App.service import create_appointment
from App.db.schemas import appointmentCreate, appointment_schema
from App.db.client import db_client



router = APIRouter(
    prefix= "/appointment",
    tags=["appointment"]
)


@router.get("/appoinments")
async def get_appointment():
    appointments = list(db_client.appointments.find())
    return appointments



@router.post("/new_appointment")
async def new_appointment(appointment : appointmentCreate):
    new_appoint =create_appointment(**appointment.model_dump())
    return new_appoint




