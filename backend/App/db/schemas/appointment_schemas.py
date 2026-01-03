from pydantic import BaseModel
from datetime import datetime, time

class AppointmentCreate(BaseModel):
    appointment_start: datetime
    availability_start: time
    availability_end: time
    provider_id: str
    business_id: str
    client_id: str
    service_id: str    
    notes: str | None = None

class PatchUpdateAppointment(BaseModel):
    appointment_start: datetime | None = None
    availability_start: time | None = None
    availability_end: time | None = None
    provider_id: str | None = None
    business_id: str | None = None
    client_id: str | None = None
    service_id: str | None = None    
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
