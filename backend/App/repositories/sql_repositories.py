import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from App.db.models import Business, User

from .repositories import BusinessRepository, UserRepository


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
