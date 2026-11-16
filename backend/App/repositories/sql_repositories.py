import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models import Business, User
from App.db.models.business_members import BusinessMembers
from App.db.models.service import Service

from .repositories import (
    BusinessMemberRepository,
    BusinessRepository,
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


class SQLModelBusinessMembersRepository(BusinessMemberRepository):
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
