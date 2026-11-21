import uuid

from fastapi import HTTPException, status

from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.repositories.appointment import AppointmentRepository
from App.repositories.appointment_history import AppointmentStatusHistoryRepository
from App.repositories.service_repository import ServiceRepository


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
        appointment = self.appointments.get(appointment_id)

        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Appointment not found"},
            )

        service = self.appointments.get_by_business(
            appointment_id=appointment.id, business_id=business_id
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Appointment not found"},
            )

        return self.repo.list_by_appointment(
            appointment_id=appointment.id,
            limit=limit,
            offset=offset,
        )
