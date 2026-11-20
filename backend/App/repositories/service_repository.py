
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from App.db.models.service import Service


class ServiceRepository(ABC):
    @abstractmethod
    def get(self, service_id: uuid.UUID) -> Service | None:
        pass

    @abstractmethod
    def add(self, service: Service) -> Service:
        pass

    @abstractmethod
    def update(self, service: Service, changes: dict) -> Service:
        pass

    @abstractmethod
    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Service]:
        pass


class SQLServiceRepository(ServiceRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, service_id: uuid.UUID) -> Service | None:
        return self.session.get(Service, service_id)

    def add(self, service: Service) -> Service:
        self.session.add(service)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(service)
        return service

    def update(self, service: Service, changes: dict) -> Service:
        service.sqlmodel_update(changes)
        self.session.add(service)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(service)
        return service

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Service]:
        statement = (
            select(Service)
            .where(Service.business_id == business_id)
            .order_by(Service.name)
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(Service.active == active)
        return list(self.session.exec(statement).all())
