import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.business_members import (
    BusinessMembers,
    BusinessMembersCreate,
    BusinessMembersUpdate,
)
from App.repositories.repositories import (
    BusinessMemberRepository,
    BusinessRepository,
    UserRepository,
)
from App.service.errors import conflict_message

UNIQUE_MESSAGES = {
    "business_members_user_business_unique": "Business with that user or business already exists",
    "business_member_has_role": "Business members has to have a role",
}


class BusinessMemberService:
    def __init__(
        self,
        repo: BusinessMemberRepository,
        user_repo: UserRepository,
        business_repo: BusinessRepository,
    ):
        self.repo = repo
        self.user_repo = user_repo
        self.business_repo = business_repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def create(
        self, business_id: uuid.UUID, data: BusinessMembersCreate
    ) -> BusinessMembers:
        business = self.business_repo.get(business_id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business Not found"},
            )
        user = self.user_repo.get(data.user_id)
        if user is None or not user.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "User Not found"},
            )

        member = BusinessMembers(**data.model_dump(), business_id=business_id)

        try:
            return self.repo.add(member)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def get(self, business_id: uuid.UUID, member_id: uuid.UUID) -> BusinessMembers:
        business_member = self.repo.get(member_id)
        if business_member is None or business_member.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business Member not found"},
            )
        return business_member

    def update(
        self, business_id: uuid.UUID, member_id: uuid.UUID, data: BusinessMembersUpdate
    ) -> BusinessMembers:
        business_member = self.get(business_id, member_id)

        if business_member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business not found"},
            )

        changes = data.model_dump(exclude_unset=True)
        is_admin = changes.get("is_admin", business_member.is_admin)
        is_provider = changes.get("is_provider", business_member.is_provider)

        if not (is_admin or is_provider):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "A member must be an admin, provide or both"},
            )

        try:
            return self.repo.update(business_member, changes)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[BusinessMembers]:
        if self.business_repo.get(business_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Error": "Business not found"},
            )
        return self.repo.list_by_business(
            business_id, active=active, limit=limit, offset=offset
        )
