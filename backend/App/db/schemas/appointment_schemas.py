from datetime import datetime

from pydantic import BaseModel

from App.db.models import StatusAppointments


class AppointmentBase(BaseModel):
    appointment_start: datetime
    client_id: str
    provider_id: str
    service_id: str
    business_id: str
    notes: str | None = None


class AppointmentPatch(BaseModel):
    appointment_start: datetime | None = None
    client_id: str | None = None
    provider_id: str | None = None
    service_id: str | None = None
    business_id: str | None = None
    status: StatusAppointments | None = None
    notes: str | None = None


def appointment_to_dict(appointment) -> dict:
    return {
        "id": str(appointment["_id"]),
        "client_id": str(appointment["client_id"]),
        "provider_id": str(appointment["provider_id"]),
        "service_id": str(appointment["service_id"]),
        "business_id": str(appointment["business_id"]),
        "appointment_start": appointment["appointment_start"],
        "end_time": appointment["end_time"],
        "status": appointment.get("status"),
        "notes": appointment.get("notes"),
    }


def appointments_to_dict(appointments) -> list:
    result = []

    for appointment in appointments:
        result.append(appointment_to_dict(appointment))
    return result


class AppointmentCreate(AppointmentBase):
    pass


class PutAppointment(AppointmentBase):
    pass
