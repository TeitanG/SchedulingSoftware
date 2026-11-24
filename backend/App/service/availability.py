import uuid

from fastapi import HTTPException, status

from App.db.models.availability import (
    Availability,
    AvailabilityCreate,
    AvailabilityUpdate,
)
from App.db.models.business_members import BusinessMembers
from App.repositories.availability import AvailabilityRepository
from App.repositories.business_member import BusinessMemberRepository
from App.service.errors import response_404


class AvailabilityService:
    def __init__(
        self, repo: AvailabilityRepository, member_repo: BusinessMemberRepository
    ):
        self.repo = repo
        self.member_repo = member_repo

    def _get_member(
        self, business_id: uuid.UUID, member_id: uuid.UUID
    ) -> BusinessMembers:
        member = self.member_repo.get(member_id)
        if member is None or member.business_id != business_id:
            raise response_404("Member")
        return member

    def get(
        self, business_id: uuid.UUID, member_id: uuid.UUID, availability_id: uuid.UUID
    ) -> Availability:
        self._get_member(business_id, member_id)
        availability = self.repo.get(availability_id)
        if availability is None or availability.member_id != member_id:
            raise response_404("Availability")
        return availability

    def create(
        self, business_id: uuid.UUID, member_id: uuid.UUID, data: AvailabilityCreate
    ) -> Availability:
        member = self._get_member(business_id, member_id)

        if not member.is_provider:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "This member is not a provider"},
            )

        if not member.active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Member is not active"},
            )
        if data.active:
            overlapping = self.repo.find_overlapping(
                member_id, data.day, data.start_time, data.end_time
            )
            if overlapping is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"Error": "This availability overlaps with an existing one"},
                )

        availability = Availability(**data.model_dump(), member_id=member.id)
        return self.repo.add(availability)

    def list_by_member(
        self,
        business_id: uuid.UUID,
        member_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Availability]:
        self._get_member(business_id=business_id, member_id=member_id)
        return self.repo.list_by_member(
            member_id, active=active, limit=limit, offset=offset
        )

    def update(
        self,
        business_id: uuid.UUID,
        member_id: uuid.UUID,
        availability_id: uuid.UUID,
        data: AvailabilityUpdate,
    ) -> Availability:
        availability = self.get(business_id, member_id, availability_id)
        changes = data.model_dump(exclude_unset=True)

        day = changes.get("day", availability.day)
        start_time = changes.get("start_time", availability.start_time)
        end_time = changes.get("end_time", availability.end_time)
        active = changes.get("active", availability.active)

        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "start_time must be before end_time"},
            )

        if active:
            overlapping = self.repo.find_overlapping(
                member_id, day, start_time, end_time, excluded_id=availability.id
            )
            if overlapping is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"Error": "This availability overlaps with an existing one"},
                )

        return self.repo.update(availability, changes)
