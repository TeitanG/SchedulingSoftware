from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from App.db.engine import get_session
from App.repositories.appointment import SQLAppointmentRepository
from App.repositories.appointment_history import SQLAppointmentStatusHistoryRepository
from App.repositories.availability import SQLAvailabilityRepository
from App.repositories.business import SQLBusinessRepository
from App.repositories.business_member import SQLBusinessMembersRepository
from App.repositories.customer import SQLCustomerRepository
from App.repositories.provider_service import SQLProviderServiceRepository
from App.repositories.service_repository import SQLServiceRepository
from App.repositories.user import SQLUserRepository
from App.service.appointment import AppointmentService
from App.service.appointment_history import AppointmentStatusHistoryService
from App.service.availability import AvailabilityService
from App.service.business import BusinessService
from App.service.business_member import BusinessMemberService
from App.service.customer import CustomerService
from App.service.service import CatalogService
from App.service.service_provider import ServiceProviderService
from App.service.user import UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_business_service(session: SessionDep) -> BusinessService:
    return BusinessService(SQLBusinessRepository(session))


def get_user_service(session: SessionDep) -> UserService:
    return UserService(SQLUserRepository(session))


def get_business_member_service(session: SessionDep) -> BusinessMemberService:
    return BusinessMemberService(
        SQLBusinessMembersRepository(session),
        SQLUserRepository(session),
        SQLBusinessRepository(session),
    )


def get_service_service(session: SessionDep) -> CatalogService:
    return CatalogService(
        SQLServiceRepository(session),
        SQLBusinessRepository(session),
    )


def get_provider_service(session: SessionDep) -> ServiceProviderService:
    return ServiceProviderService(
        SQLProviderServiceRepository(session),
        SQLServiceRepository(session),
        SQLBusinessMembersRepository(session),
    )


def get_availability_service(session: SessionDep) -> AvailabilityService:
    return AvailabilityService(
        SQLAvailabilityRepository(session),
        SQLBusinessMembersRepository(session),
    )


def get_customer_service(session: SessionDep) -> CustomerService:
    return CustomerService(
        SQLCustomerRepository(session), SQLBusinessRepository(session)
    )


def get_appointment_service(session: SessionDep) -> AppointmentService:
    return AppointmentService(
        SQLAppointmentRepository(session),
        SQLBusinessMembersRepository(session),
        SQLServiceRepository(session),
        SQLProviderServiceRepository(session),
        SQLAvailabilityRepository(session),
        SQLBusinessRepository(session),
        SQLCustomerRepository(session),
    )


def get_appointment_history_service(
    session: SessionDep,
) -> AppointmentStatusHistoryService:
    return AppointmentStatusHistoryService(
        SQLAppointmentStatusHistoryRepository(session),
        SQLAppointmentRepository(session),
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
BusinessServiceDep = Annotated[BusinessService, Depends(get_business_service)]
BusinessMemberServiceDep = Annotated[
    BusinessMemberService, Depends(get_business_member_service)
]
ServiceServiceDep = Annotated[CatalogService, Depends(get_service_service)]
ProviderServiceDep = Annotated[ServiceProviderService, Depends(get_provider_service)]
AvailabilityServiceDep = Annotated[
    AvailabilityService, Depends(get_availability_service)
]
CustomerServiceDep = Annotated[CustomerService, Depends(get_customer_service)]
AppointmentServiceDep = Annotated[AppointmentService, Depends(get_appointment_service)]
AppointmentStatusHistoryServiceDep = Annotated[
    AppointmentStatusHistoryService, Depends(get_appointment_history_service)
]
