import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, func, select

from App.db.models.appointment import Appointment
from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.db.models.common import AppointmentStatus
from App.db.models.service import Service


class AppointmentRepository(ABC):
    @abstractmethod
    def get(self, appointment_id: uuid.UUID) -> Appointment | None:
        pass

    @abstractmethod
    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        status: AppointmentStatus | None,
        limit: int,
        offset: int,
    ) -> list[Appointment]:
        pass

    @abstractmethod
    def count_overlapping(
        self, provider_id: uuid.UUID, starts_at: datetime, ends_at: datetime
    ) -> int:
        pass

    @abstractmethod
    def add_with_history(
        self, appointment: Appointment, history: AppointmentStatusHistory
    ) -> Appointment:
        pass

    @abstractmethod
    def update_status(
        self, appointment: Appointment, history: AppointmentStatusHistory
    ) -> Appointment:
        pass


class SQLAppointmentRepository(AppointmentRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, appointment_id: uuid.UUID) -> Appointment | None:
        return self.session.get(Appointment, appointment_id)

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        status: AppointmentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Appointment]:
        statement = (
            select(Appointment)
            .join(Service, col(Service.id) == col(Appointment.service_id))
            .where(Service.business_id == business_id)
        )

        if status is not None:
            statement = statement.where(Appointment.status == status)

        statement = (
            statement.order_by(col(Appointment.starts_at)).offset(offset).limit(limit)
        )

        return list(self.session.exec(statement).all())

    def count_overlapping(
        self, provider_id: uuid.UUID, starts_at: datetime, ends_at: datetime
    ) -> int:
        statement = (
            select(func.count())
            .select_from(Appointment)
            .where(
                Appointment.provider_id == provider_id,
                col(Appointment.starts_at) < ends_at,
                col(Appointment.ends_at) > starts_at,
                col(Appointment.status).in_(
                    [AppointmentStatus.pending, AppointmentStatus.confirmed]
                ),
            )
        )
        return self.session.exec(statement).one()

    def add_with_history(
        self, appointment: Appointment, history: AppointmentStatusHistory
    ) -> Appointment:
        self.session.add(appointment)
        self.session.add(history)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(appointment)
        return appointment

    def update_status(
        self, appointment: Appointment, history: AppointmentStatusHistory
    ) -> Appointment:
        appointment.status = history.new_status

        self.session.add(appointment)
        self.session.add(history)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

        self.session.refresh(appointment)
        return appointment
