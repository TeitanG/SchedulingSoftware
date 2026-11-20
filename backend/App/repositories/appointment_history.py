import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.appointment_status_history import AppointmentStatusHistory


class AppointmentStatusHistoryRepository(ABC):
    @abstractmethod
    def list_by_appointment(
        self, appointment_id: uuid.UUID, limit: int, offset: int
    ) -> list[AppointmentStatusHistory]:
        pass


class SQLAppointmentStatusHistoryRepository(AppointmentStatusHistoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_by_appointment(
        self, appointment_id: uuid.UUID, limit: int, offset: int
    ) -> list[AppointmentStatusHistory]:
        statement = (
            select(AppointmentStatusHistory)
            .where(AppointmentStatusHistory.appointment_id == appointment_id)
            .order_by(col(AppointmentStatusHistory.changed_at))
            .limit(limit)
            .offset(offset)
        )

        return list(self.session.exec(statement).all())
