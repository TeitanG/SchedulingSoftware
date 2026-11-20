import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.business_members import BusinessMembers


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

    def lock_provider(self, provider_id: uuid.UUID) -> BusinessMembers | None:
        statement = (
            select(BusinessMembers)
            .where(BusinessMembers.id == provider_id)
            .with_for_update()
        )
        return self.session.exec(statement).one_or_none()
