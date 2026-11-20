import uuid
from abc import ABC, abstractmethod
from datetime import time

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.availability import Availability
from App.db.models.common import DaysOfTheWeek


class AvailabilityRepository(ABC):
    @abstractmethod
    def get(self, availability_id: uuid.UUID) -> Availability | None:
        pass

    @abstractmethod
    def add(self, availability: Availability) -> Availability:
        pass

    @abstractmethod
    def update(self, availability: Availability, changes: dict) -> Availability:
        pass

    @abstractmethod
    def list_by_member(
        self,
        member_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Availability]:
        pass

    @abstractmethod
    def find_overlapping(
        self,
        member_id: uuid.UUID,
        day: DaysOfTheWeek,
        start_time: time,
        end_time: time,
        excluded_id: uuid.UUID | None = None,
    ) -> Availability | None:
        pass

    @abstractmethod
    def list_active_by_member_and_day(
        self,
        member_id: uuid.UUID,
        day: DaysOfTheWeek,
    ) -> list[Availability]:
        pass


class SQLAvailabilityRepository(AvailabilityRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, availability_id: uuid.UUID) -> Availability | None:
        return self.session.get(Availability, availability_id)

    def add(self, availability: Availability) -> Availability:
        self.session.add(availability)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(availability)
        return availability

    def update(self, availability: Availability, changes: dict) -> Availability:
        availability.sqlmodel_update(changes)
        self.session.add(availability)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(availability)
        return availability

    def list_by_member(
        self,
        member_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Availability]:
        statement = (
            select(Availability)
            .where(Availability.member_id == member_id)
            .order_by(Availability.day, col(Availability.start_time))
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(Availability.active == active)
        return list(self.session.exec(statement).all())

    def find_overlapping(
        self,
        member_id: uuid.UUID,
        day: DaysOfTheWeek,
        start_time: time,
        end_time: time,
        excluded_id: uuid.UUID | None = None,
    ) -> Availability | None:
        statement = select(Availability).where(
            Availability.member_id == member_id,
            Availability.day == day,
            Availability.active == True,
            Availability.start_time < end_time,
            Availability.end_time > start_time,
        )
        if excluded_id is not None:
            statement = statement.where(Availability.id != excluded_id)
        return self.session.exec(statement).first()

    def list_active_by_member_and_day(
        self,
        member_id: uuid.UUID,
        day: DaysOfTheWeek,
    ) -> list[Availability]:
        statement = (
            select(
                Availability,
            )
            .where(
                Availability.member_id == member_id,
                Availability.day == day,
                Availability.active == True,
            )
            .order_by(col(Availability.start_time))
        )
        return list(self.session.exec(statement).all())
