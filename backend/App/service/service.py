import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.service import Service, ServiceCreate, ServiceUpdate
from App.repositories.business import BusinessRepository
from App.repositories.service_repository import ServiceRepository
from App.service.errors import conflict_message

UNIQUE_MESSAGES = {
    "services_business_name_unique": "Business already have a service with this name",
}


class ServiceService:
    def __init__(self, repo: ServiceRepository, business_repo: BusinessRepository):
        self.repo = repo
        self.business_repo = business_repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def create(self, business_id: uuid.UUID, data: ServiceCreate) -> Service:
        business = self.business_repo.get(business_id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business not found"},
            )

        if not business.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Business is currently inactive"},
            )
        service = Service(**data.model_dump(), business_id=business_id)

        try:
            return self.repo.add(service)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def get(self, business_id: uuid.UUID, service_id: uuid.UUID) -> Service:
        service = self.repo.get(service_id)
        if service is None or service.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Service not found"},
            )
        return service

    def update(
        self, business_id: uuid.UUID, service_id: uuid.UUID, data: ServiceUpdate
    ) -> Service:
        service = self.get(business_id, service_id)
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Service Not found"},
            )
        changes = data.model_dump(exclude_unset=True)

        try:
            return self.repo.update(service, changes)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Service]:
        business = self.business_repo.get(business_id)

        if business is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Business not found"},
            )
        if not business.active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return self.repo.list_by_business(
            business_id, active=active, limit=limit, offset=offset
        )
