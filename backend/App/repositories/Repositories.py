# noqa: N999
import uuid
from abc import ABC, abstractmethod

from App.db.models import Business


class UserRepository(ABC):
    @abstractmethod
    def something(self):
        pass

    #!todo  # noqa: EXE005


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


class ServiceRepository(ABC):
    @abstractmethod
    def something(self):
        pass

    #!todo  # noqa: EXE005


class AppointmentRepository(ABC):
    @abstractmethod
    def something(self):
        pass

    #!todo  # noqa: EXE005


class AvailabilityRepository(ABC):
    @abstractmethod
    def find_by_provider():
        pass

    #!todo  # noqa: EXE005
