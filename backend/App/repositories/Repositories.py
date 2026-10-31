# noqa: N999
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from App.db.models import (
    BusinessType,
    StatusAppointments,
    daysOfTheWeek,
    user_Status,
    user_Type,
)


class Repository(ABC):
    @abstractmethod
    def find_by_id(self, entity_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def find_one(self, query: dict) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def find_all(self, query: dict | None = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def save(self, entity: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def update(self, entity_id: str, data: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass


class UserRepository(Repository):
    @abstractmethod
    def find_by_username(self, username: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def find_by_role(self, role: user_Type) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_status(self, status: user_Status) -> list[dict[str, Any]]:
        pass


class BusinessRepository(Repository):
    @abstractmethod
    def find_by_name(self, name: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def find_active(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_type(self, type: BusinessType) -> list[dict[str, Any]]:
        pass


class ServiceRepository(Repository):
    @abstractmethod
    def find_by_provider(
        self, provider_id: str, date_range: tuple[datetime, datetime] | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> dict[str, Any] | None:
        pass


class AppointmentRepository(Repository):
    @abstractmethod
    def find_by_provider(
        self, provider_id: str, date_range: tuple[datetime, datetime] | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_client(
        self, client_id: str, date_range: tuple | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_overlapping(
        self, provider_id: str, start_time: datetime, end_time: datetime
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_status(self, status: StatusAppointments) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_pending_and_confirmed(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def existing_appointments(
        self, provider_id: str, business_id: str
    ) -> list[dict[str, Any]]:
        pass


class AvailabilityRepository(Repository):
    @abstractmethod
    def find_by_provider(
        self, provider_id: str, date_range: tuple[datetime, datetime] | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_active_by_business(self, business_id: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def find_overlapping_availability(
        self,
        availability_id: str,
        provider_id: str,
        business_id: str,
        day: daysOfTheWeek,
        start_time: datetime,
        end_time: datetime,
    ) -> dict[str, Any] | None:
        pass
