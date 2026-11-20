import secrets
import uuid
from datetime import timedelta
from typing import NoReturn
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.appointment import Appointment, AppointmentCreate
from App.db.models.appointment_status_history import AppointmentStatusHistory
from App.db.models.common import WEEKDAYS, AppointmentStatus, utc_now
from App.repositories.appointment import AppointmentRepository
from App.repositories.availability import AvailabilityRepository
from App.repositories.business import BusinessRepository
from App.repositories.business_member import BusinessMemberRepository
from App.repositories.provider_service import ProviderServiceRepository
from App.repositories.service_repository import ServiceRepository
from App.repositories.user import UserRepository
from App.service.errors import conflict_message

UNIQUE_MESSAGES = {
    "appointments_starts_before_ends": "Start date and time must be before the end date and time"
}

BOOKING_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generate_booking_code():
    charts = "".join(secrets.choice(BOOKING_CODE_ALPHABET) for _ in range(6))
    return f"{charts[:4]}-{charts[3:]}"


class AppointmentService:
    def __init__(
        self,
        appointments: AppointmentRepository,
        members: BusinessMemberRepository,
        services: ServiceRepository,
        providers_services: ProviderServiceRepository,
        availabilities: AvailabilityRepository,
        business: BusinessRepository,
        users: UserRepository,
    ):
        self.repo = appointments
        self.members = members
        self.services = services
        self.providers_services = providers_services
        self.availabilities = availabilities
        self.business = business
        self.users = users

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

        user = self.users.get(data.client_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "The client does not exist"},
            )

        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "This client is not active"},
            )
        ends_at = data.starts_at + timedelta(minutes=service.duration)

        if data.starts_at <= ends_at:
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

        if overlapping > service.capacity:
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
            changed_by=data.client_id,
        )

        try:
            return self.repo.add_with_history(appointment, history)
        except IntegrityError as error:
            self._raise_if_conflict(error)
