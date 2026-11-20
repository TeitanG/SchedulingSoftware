import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.provider_service import ProviderService


class ProviderServiceRepository(ABC):
    @abstractmethod
    def get(
        self, member_id: uuid.UUID, service_id: uuid.UUID
    ) -> ProviderService | None:
        pass

    @abstractmethod
    def add(
        self,
        provider_service: ProviderService,
    ) -> ProviderService:
        pass

    @abstractmethod
    def delete(self, provider_service: ProviderService) -> None:
        pass

    @abstractmethod
    def list_by_service(
        self, service_id: uuid.UUID, *, limit: int = 50, offset: int = 0
    ) -> list[ProviderService]:
        pass


class SQLProviderServiceRepository(ProviderServiceRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(
        self, member_id: uuid.UUID, service_id: uuid.UUID
    ) -> ProviderService | None:
        return self.session.get(
            ProviderService, {"member_id": member_id, "service_id": service_id}
        )

    def add(self, provider_service: ProviderService) -> ProviderService:
        self.session.add(provider_service)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(provider_service)
        return provider_service

    def delete(self, provider_service: ProviderService) -> None:
        self.session.delete(provider_service)
        self.session.commit()

    def list_by_service(
        self, service_id: uuid.UUID, *, limit: int = 50, offset: int = 0
    ) -> list[ProviderService]:
        statement = (
            select(ProviderService)
            .where(ProviderService.service_id == service_id)
            .order_by(col(ProviderService.created_at))
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())
