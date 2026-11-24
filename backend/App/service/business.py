import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models import Business, BusinessCreate, BusinessUpdate
from App.repositories.business import BusinessRepository
from App.service.errors import conflict_message, response_404

UNIQUE_MESSAGES = {
    "businesses_name_unique": "A business with that name already exists",
    "businesses_email_unique": "A business with that email already exists",
}


class BusinessService:
    def __init__(self, repo: BusinessRepository):
        self.repo = repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def create(self, data: BusinessCreate) -> Business:
        business = Business.model_validate(data)
        try:
            return self.repo.add(business)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def get(self, business_id: uuid.UUID) -> Business:
        business = self.repo.get(business_id)
        if business is None:
            raise response_404("Business")

        return business

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Business]:
        return self.repo.list_all(active=active, limit=limit, offset=offset)

    def update(self, business_id: uuid.UUID, data: BusinessUpdate) -> Business:
        business = self.get(business_id)

        changes = data.model_dump(exclude_unset=True)
        try:
            return self.repo.update(business, changes)
        except IntegrityError as error:
            self._raise_if_conflict(error)
