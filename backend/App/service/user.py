import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models import User, UserCreate, UserUpdate
from App.repositories.user import UserRepository
from App.security import hash_password
from App.service.errors import conflict_message, response_404

UNIQUE_MESSAGES = {"users_email_unique": "A user with that email already exists"}


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def create(self, data: UserCreate) -> User:

        user = User(
            **data.model_dump(exclude={"password"}),
            password_hash=hash_password(data.password),
        )

        try:
            return self.repo.add(user)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def get(self, user_id: uuid.UUID) -> User:
        user = self.repo.get(user_id)

        if user is None:
            raise response_404("User")
        return user

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[User]:
        return self.repo.list_all(active=active, limit=limit, offset=offset)

    def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = self.get(user_id)
        changes = data.model_dump(exclude_unset=True)

        try:
            return self.repo.update(user, changes)
        except IntegrityError as error:
            self._raise_if_conflict(error)
