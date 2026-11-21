import secrets
import uuid
from datetime import timedelta
from typing import NoReturn
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentNotesUpdate,
    AppointmentStatusUpdate,
)
from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.db.models.common import WEEKDAYS, AppointmentStatus, utc_now
from App.repositories.appointment import AppointmentRepository
from App.repositories.availability import AvailabilityRepository
from App.repositories.business import BusinessRepository
from App.repositories.business_member import BusinessMemberRepository
from App.repositories.customer import CustomerRepository
from App.repositories.provider_service import ProviderServiceRepository
from App.repositories.service_repository import ServiceRepository
from App.service.errors import conflict_message

UNIQUE_MESSAGES = {
    "appointments_booking_code_unique": "Could not generate the booking code, try again",
}

BOOKING_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generate_booking_code():
    chars = "".join(secrets.choice(BOOKING_CODE_ALPHABET) for _ in range(6))
    return f"{chars[:3]}-{chars[3:]}"


ALLOWED_TRANSITIONS: dict[AppointmentStatus, set[AppointmentStatus]] = {
    AppointmentStatus.pending: {
        AppointmentStatus.confirmed,
        AppointmentStatus.canceled,
    },
    AppointmentStatus.confirmed: {
        AppointmentStatus.completed,
        AppointmentStatus.canceled,
    },
    AppointmentStatus.completed: set(),
    AppointmentStatus.canceled: set(),
}


class AppointmentService:
    def __init__(
        self,
        appointments: AppointmentRepository,
        members: BusinessMemberRepository,
        services: ServiceRepository,
        providers_services: ProviderServiceRepository,
        availabilities: AvailabilityRepository,
        business: BusinessRepository,
        customers: CustomerRepository,
    ):
        self.repo = appointments
        self.members = members
        self.services = services
        self.providers_services = providers_services
        self.availabilities = availabilities
        self.business = business
        self.customers = customers

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def create(self, business_id: uuid.UUID, data: AppointmentCreate) -> Appointment:
        business = self.business.get(business_id)

        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business not Found"},
            )

        if not business.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Business Not active"},
            )

        blocked_provider = self.members.lock_provider(data.provider_id)

        if not blocked_provider or blocked_provider.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Provider Not Found"},
            )

        if not blocked_provider.is_provider:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "The role is not provider"},
            )

        if not blocked_provider.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Provider is not active"},
            )

        service = self.services.get(data.service_id)

        if not service or service.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Service not found"},
            )

        if not service.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Service is not active"},
            )

        provider_service = self.providers_services.get(
            member_id=blocked_provider.id, service_id=service.id
        )

        if not provider_service:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "The Provider does not have this service"},
            )

        client = self.customers.get(data.client_id)

        if not client or client.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "The client does not exist"},
            )

        if not client.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "This client is not active"},
            )
        ends_at = data.starts_at + timedelta(minutes=service.duration)

        if ends_at <= data.starts_at:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Start time must be before end time"},
            )

        tz = ZoneInfo(business.timezone)
        local_start = data.starts_at.astimezone(tz)
        local_end = ends_at.astimezone(tz)

        if local_start < utc_now():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "Appointment cannot be scheduled in the past"},
            )

        if local_start.date() != local_end.date():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "Appointment cannot cross midnight"},
            )

        local_day = WEEKDAYS[local_start.weekday()]
        start_time = local_start.time()
        end_time = local_end.time()

        blocks = self.availabilities.list_active_by_member_and_day(
            member_id=blocked_provider.id,
            day=local_day,
        )
        if not any(
            block.start_time <= start_time and end_time <= block.end_time
            for block in blocks
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Provider is not available at that time"},
            )

        overlapping = self.repo.count_overlapping(
            blocked_provider.id, local_start, local_end
        )

        if overlapping >= service.capacity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "No capacity available"},
            )
        appointment = Appointment(
            **data.model_dump(), ends_at=ends_at, booking_code=generate_booking_code()
        )
        history = AppointmentStatusHistory(
            appointment_id=appointment.id,
            old_status=None,
            new_status=AppointmentStatus.pending,
        )

        try:
            return self.repo.add_with_history(appointment, history)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def get(self, business_id: uuid.UUID, appointment_id: uuid.UUID) -> Appointment:

        appointment = self.repo.get_by_business(
            appointment_id=appointment_id, business_id=business_id
        )

        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Appointment not found"},
            )
        return appointment

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        appointment_status: AppointmentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Appointment]:
        business = self.business.get(business_id)

        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business not found"},
            )

        return self.repo.list_by_business(
            business_id, status=appointment_status, limit=limit, offset=offset
        )

    def update_status(
        self,
        business_id: uuid.UUID,
        appointment_id: uuid.UUID,
        data: AppointmentStatusUpdate,
    ) -> Appointment:

        appointment = self.get(business_id=business_id, appointment_id=appointment_id)

        current = appointment.status
        new = data.status
        if new not in ALLOWED_TRANSITIONS[current]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "Error": f"Cannot change status from {current.value} to {new.value}"
                },
            )
        history = AppointmentStatusHistory(
            appointment_id=appointment.id,
            old_status=current,
            new_status=new,
            changed_by=None,  # TODO: usuario del token cuando haya login
        )
        return self.repo.update_status(appointment, history)

    def update_notes(
        self,
        business_id: uuid.UUID,
        appointment_id: uuid.UUID,
        data: AppointmentNotesUpdate,
    ) -> Appointment:
        appointment = self.get(business_id=business_id, appointment_id=appointment_id)
        return self.repo.update_notes(appointment, data.notes)
