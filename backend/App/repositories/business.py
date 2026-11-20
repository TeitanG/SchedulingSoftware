import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from App.db.models.business import Business


class BusinessRepository(ABC):
    @abstractmethod
    def get(self, business_id: uuid.UUID) -> Business | None:
        pass

    @abstractmethod
    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Business]:
        pass

    @abstractmethod
    def add(self, business: Business) -> Business:
        pass

    @abstractmethod
    def update(self, business: Business, changes: dict) -> Business:
        pass


class SQLBusinessRepository(BusinessRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, business_id: uuid.UUID) -> Business | None:
        return self.session.get(Business, business_id)

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Business]:
        statement = select(Business).order_by(Business.name).offset(offset).limit(limit)
        if active is not None:
            statement = statement.where(Business.active == active)
        return list(self.session.exec(statement).all())

    def add(self, business: Business) -> Business:
        self.session.add(business)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business)
        return business

    def update(self, business: Business, changes: dict) -> Business:
        business.sqlmodel_update(changes)
        self.session.add(business)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business)
        return business
