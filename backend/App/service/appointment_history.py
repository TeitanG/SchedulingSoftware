import uuid

from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.repositories.appointment import AppointmentRepository
from App.repositories.appointment_history import AppointmentStatusHistoryRepository
from App.service.errors import response_404


class AppointmentStatusHistoryService:
    def __init__(
        self,
        repo: AppointmentStatusHistoryRepository,
        appointments: AppointmentRepository,
    ):
        self.repo = repo
        self.appointments = appointments

    def list_by_appointment(
        self,
        business_id: uuid.UUID,
        appointment_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AppointmentStatusHistory]:

        Appointment = self.appointments.get_by_business(
            appointment_id=appointment_id, business_id=business_id
        )

        if Appointment is None:
            raise response_404("Appointment")

        return self.repo.list_by_appointment(
            appointment_id=appointment_id,
            limit=limit,
            offset=offset,
        )
