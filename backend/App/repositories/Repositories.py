import uuid
from abc import ABC, abstractmethod
from datetime import datetime, time

from App.db.models import Business
from App.db.models.appointment import Appointment
from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.db.models.availability import Availability
from App.db.models.business_members import BusinessMembers
from App.db.models.common import AppointmentStatus, DaysOfTheWeek
from App.db.models.provider_service import ProviderService
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
    def get(self, business_member_id: uuid.UUID) -> BusinessMembers | None:
        pass

    @abstractmethod
    def add(self, business_member: BusinessMembers) -> BusinessMembers:
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

    @abstractmethod
    def lock_provider(self, provider_id: uuid.UUID) -> BusinessMembers | None:
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


class AppointmentStatusHistoryRepository(ABC):
    @abstractmethod
    def list_by_appointment(
        self, appointment_id: uuid.UUID, limit: int, offset: int
    ) -> list[AppointmentStatusHistory]:
        pass
