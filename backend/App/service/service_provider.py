import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.business_members import BusinessMembers
from App.db.models.provider_service import ProviderService, ProviderServiceCreate
from App.db.models.service import Service
from App.repositories.repositories import (
    BusinessMemberRepository,
    ProviderServiceRepository,
    ServiceRepository,
)
from App.service.errors import conflict_message

UNIQUE_MESSAGES = {
    "provider_services_pkey": "This member already provides this service",
}


class ServiceProviderService:
    def __init__(
        self,
        repo: ProviderServiceRepository,
        service_repo: ServiceRepository,
        member_repo: BusinessMemberRepository,
    ) -> None:
        self.repo = repo
        self.service_repo = service_repo
        self.member_repo = member_repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def _get_service(self, business_id: uuid.UUID, service_id: uuid.UUID) -> Service:
        service = self.service_repo.get(service_id)
        if service is None or service.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Service not found"},
            )
        return service

    def _get_member(
        self, business_id: uuid.UUID, member_id: uuid.UUID
    ) -> BusinessMembers:
        member = self.member_repo.get(member_id)
        if member is None or member.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Member not found"},
            )
        return member

    def add_provider(
        self, business_id: uuid.UUID, service_id: uuid.UUID, data: ProviderServiceCreate
    ) -> ProviderService:
        service = self._get_service(business_id, service_id)
        member = self._get_member(business_id, data.member_id)

        if not member.is_provider:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "Member is not a provider"},
            )
        if not member.active or not service.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Member and service must be active"},
            )
        provider_service = ProviderService(member_id=member.id, service_id=service.id)
        try:
            return self.repo.add(provider_service)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def list_providers(
        self,
        business_id: uuid.UUID,
        service_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProviderService]:
        self._get_service(business_id, service_id)
        return self.repo.list_by_service(service_id, limit=limit, offset=offset)

    def remove_provider(
        self, business_id: uuid.UUID, service_id: uuid.UUID, member_id: uuid.UUID
    ) -> None:
        self._get_service(business_id, service_id)
        provider_service = self.repo.get(member_id, service_id)
        if provider_service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "This member does not provide this service"},
            )
        self.repo.delete(provider_service)
