import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.user import User, UserCreate, UserPublic, UserUpdate
from App.dependencies.dependencies import UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(service: UserServiceDep, data: UserCreate) -> User:
    return service.create(data)


@router.get("/", response_model=list[UserPublic])
def list_users(
    service: UserServiceDep,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[User]:
    return service.list_all(active=active, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    service: UserServiceDep,
    user_id: uuid.UUID,
) -> User:
    return service.get(user_id)


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    service: UserServiceDep,
    user_id: uuid.UUID,
    data: UserUpdate,
) -> User:
    return service.update(user_id, data)
