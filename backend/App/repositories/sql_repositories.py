import uuid
from datetime import time

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models import Business, User
from App.db.models.availability import Availability, DaysOfTheWeek
from App.db.models.business_members import BusinessMembers
from App.db.models.provider_service import ProviderService
from App.db.models.service import Service

from .repositories import (
    AvailabilityRepository,
    BusinessMemberRepository,
    BusinessRepository,
    ProviderServiceRepository,
    ServiceRepository,
    UserRepository,
)


class SQLBusinessRepository(BusinessRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, business_id: uuid.UUID) -> Business | None:
        return self.session.get(Business, business_id)

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Business]:
        statement = select(Business).order_by(Business.name).offset(offset).limit(limit)
        if active is not None:
            statement = statement.where(Business.active == active)
        return list(self.session.exec(statement).all())

    def add(self, business: Business) -> Business:
        self.session.add(business)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business)
        return business

    def update(self, business: Business, changes: dict) -> Business:
        business.sqlmodel_update(changes)
        self.session.add(business)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business)
        return business


class SQLUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.session.get(User, user_id)

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[User]:
        statement = select(User).order_by(User.name).offset(offset).limit(limit)
        if active is not None:
            statement = statement.where(User.active == active)
        return list(self.session.exec(statement).all())

    def add(self, user: User) -> User:
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(user)
        return user

    def update(self, user: User, changes: dict) -> User:
        user.sqlmodel_update(changes)
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(user)
        return user


class SQLBusinessMembersRepository(BusinessMemberRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, business_member_id: uuid.UUID) -> BusinessMembers | None:
        return self.session.get(BusinessMembers, business_member_id)

    def add(self, business_member: BusinessMembers) -> BusinessMembers:
        self.session.add(business_member)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business_member)
        return business_member

    def update(
        self, business_member: BusinessMembers, changes: dict
    ) -> BusinessMembers:
        business_member.sqlmodel_update(changes)
        self.session.add(business_member)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business_member)
        return business_member

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BusinessMembers]:
        statement = (
            select(BusinessMembers)
            .where(BusinessMembers.business_id == business_id)
            .order_by(col(BusinessMembers.created_at))
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(BusinessMembers.active == active)
        return list(self.session.exec(statement).all())


class SQLServiceRepository(ServiceRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, service_id: uuid.UUID) -> Service | None:
        return self.session.get(Service, service_id)

    def add(self, service: Service) -> Service:
        self.session.add(service)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(service)
        return service

    def update(self, service: Service, changes: dict) -> Service:
        service.sqlmodel_update(changes)
        self.session.add(service)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(service)
        return service

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Service]:
        statement = (
            select(Service)
            .where(Service.business_id == business_id)
            .order_by(Service.name)
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(Service.active == active)
        return list(self.session.exec(statement).all())


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


class SQLAvailabilityRepository(AvailabilityRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, availability_id: uuid.UUID) -> Availability | None:
        return self.session.get(Availability, availability_id)

    def add(self, availability: Availability) -> Availability:
        self.session.add(availability)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(availability)
        return availability

    def update(self, availability: Availability, changes: dict) -> Availability:
        availability.sqlmodel_update(changes)
        self.session.add(availability)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(availability)
        return availability

    def find_overlapping(
        self,
        member_id: uuid.UUID,
        day: DaysOfTheWeek,
        start_time: time,
        end_time: time,
        excluded_id: uuid.UUID | None = None,
    ) -> Availability | None:
        statement = select(Availability).where(
            Availability.member_id == member_id,
            Availability.day == day,
            Availability.active == True,
            Availability.start_time < end_time,
            Availability.end_time > start_time,
        )
        if excluded_id is not None:
            statement = statement.where(Availability.id != excluded_id)
        return self.session.exec(statement).first()

    def list_by_member(
        self,
        member_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Availability]:
        statement = (
            select(Availability)
            .where(Availability.member_id == member_id)
            .order_by(Availability.day, col(Availability.start_time))
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(Availability.active == active)
        return list(self.session.exec(statement).all())
