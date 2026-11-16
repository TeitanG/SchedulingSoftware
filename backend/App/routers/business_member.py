import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.business_members import (
    BusinessMembers,
    BusinessMembersCreate,
    BusinessMembersPublic,
    BusinessMembersUpdate,
)
from App.dependencies.dependencies import BusinessMemberServiceDep

router = APIRouter(prefix="/business/{business_id}/members", tags=["Business_members"])


@router.post(
    "/", response_model=BusinessMembersPublic, status_code=status.HTTP_201_CREATED
)
def create_business_member(
    business_id: uuid.UUID,
    data: BusinessMembersCreate,
    service: BusinessMemberServiceDep,
) -> BusinessMembers:
    return service.create(business_id, data)


@router.get("/", response_model=list[BusinessMembersPublic])
def list_business_members(
    service: BusinessMemberServiceDep,
    business_id: uuid.UUID,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[BusinessMembers]:
    return service.list_by_business(
        business_id, active=active, limit=limit, offset=offset
    )


@router.get("/{member_id}", response_model=BusinessMembersPublic)
def get_business_member(
    business_id: uuid.UUID, member_id: uuid.UUID, service: BusinessMemberServiceDep
) -> BusinessMembers:
    return service.get(business_id, member_id)


@router.patch("/{member_id}", response_model=BusinessMembersPublic)
def patch_business_member(
    service: BusinessMemberServiceDep,
    business_id: uuid.UUID,
    member_id: uuid.UUID,
    data: BusinessMembersUpdate,
) -> BusinessMembers:
    return service.update(business_id, member_id, data)
