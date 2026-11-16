import uuid
from abc import ABC, abstractmethod

from App.db.models import Business
from App.db.models.business_members import BusinessMembers
from App.db.models.service import Service
from App.db.models.user import User


class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: uuid.UUID) -> User | None:
        pass

    @abstractmethod
    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[User]:
        pass

    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User, changes: dict) -> User:
        pass


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


class BusinessMemberRepository(ABC):
    @abstractmethod
    def get(self, business_member_id: uuid.UUID) -> BusinessMembers:
        pass

    @abstractmethod
    def add(self, data: BusinessMembers) -> BusinessMembers:
        pass

    @abstractmethod
    def update(
        self, business_member: BusinessMembers, changes: dict
    ) -> BusinessMembers:
        pass

    @abstractmethod
    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BusinessMembers]:
        pass


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
