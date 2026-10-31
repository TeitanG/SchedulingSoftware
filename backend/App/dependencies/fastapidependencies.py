from fastapi import Depends

from App.dependencies import (
    get_appointment_repository,
    get_availability_repository,
    get_service_repository,
    get_user_repository,
)
from App.repositories import (
    AppointmentRepository,
    AvailabilityRepository,
    ServiceRepository,
    UserRepository,
)
from App.service.appointment_service import AppointmentService


def get_appointment_services(
    appointment_repo: AppointmentRepository = Depends(get_appointment_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    service_repo: ServiceRepository = Depends(get_service_repository),
    availability_repo: AvailabilityRepository = Depends(get_availability_repository),
):
    return AppointmentService(
        appointment_repo,
        user_repo,
        service_repo,
        availability_repo,
    )
