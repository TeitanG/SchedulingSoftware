from pydantic import BaseModel
from datetime import datetime, time
from App.db.models import StatusAppointments

class AppointmentBase(BaseModel):
    appointment_start : datetime
    client_id: str
    provider_id: str
    service_id:str
    business_id: str
    start_time:datetime
    end_time: datetime | None = None
    status_ : StatusAppointments
    notes: str |None = None

   

class AppointmentPatch(BaseModel):
    appointment_start : datetime | None = None
    client_id: str | None = None
    provider_id: str | None = None
    service_id:str | None = None
    business_id: str | None = None
    start_time:datetime | None = None
    end_time: datetime | None = None
    status_ : StatusAppointments | None = None
    notes: str | None = None

def appointment_to_dict(appointment) -> dict:
    return {
        "id": str(appointment["_id"]),
        "client_id": str(appointment["client_id"]),
        "provider_id": str(appointment["provider_id"]),
        "service_id": str(appointment["service_id"]),
        "business_id": str(appointment["business_id"]),
        "start_time": appointment["start_time"],
        "end_time": appointment["end_time"],
        "duration": appointment["duration"],
        "status": appointment["status"],
        "notes": appointment.get("notes")
    }

class AppointmentCreate(AppointmentBase):
    pass

class PutAppointment(AppointmentBase):
    pass


