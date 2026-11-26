import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, func, select

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

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass


class SQLUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.session.get(User, user_id)

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[User]:
        statement = (
            select(User).order_by(User.name, col(User.id)).offset(offset).limit(limit)
        )
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

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.lower())

        return self.session.exec(statement).one_or_none()
