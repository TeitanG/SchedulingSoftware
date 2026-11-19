from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from App.db.engine import get_session
from App.repositories.sql_repositories import (
    SQLAvailabilityRepository,
    SQLBusinessMembersRepository,
    SQLBusinessRepository,
    SQLProviderServiceRepository,
    SQLServiceRepository,
    SQLUserRepository,
)
from App.service.availability import AvailabilityService
from App.service.business import BusinessService
from App.service.business_member import BusinessMemberService
from App.service.service import ServiceService
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


def get_service_service(session: SessionDep) -> ServiceService:
    return ServiceService(
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


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
BusinessServiceDep = Annotated[BusinessService, Depends(get_business_service)]
BusinessMemberServiceDep = Annotated[
    BusinessMemberService, Depends(get_business_member_service)
]
ServiceServiceDep = Annotated[ServiceService, Depends(get_service_service)]
ProviderServiceDep = Annotated[ServiceProviderService, Depends(get_provider_service)]
AvailabilityServiceDep = Annotated[
    AvailabilityService, Depends(get_availability_service)
]
