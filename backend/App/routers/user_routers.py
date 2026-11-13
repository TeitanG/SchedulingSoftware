from fastapi import APIRouter, Depends, status

from App.db.schemas import UserCreate, UserPatch, UserPut
from App.dependencies import get_user_repository
from App.repositories import UserRepository
from App.service import (
    create_user,
    delete_users,
    get_all_users,
    get_user_by_id,
    patch_users,
    put_user,
)

router = APIRouter(prefix="/users", tags=["usuarios"])


@router.get("/")
async def get_users(user_repo: UserRepository = Depends(get_user_repository)):

    return get_all_users(user_repo)


@router.get("/{id}")
async def get_user(id: str, user_repo: UserRepository = Depends(get_user_repository)):

    return get_user_by_id(id, user_repo)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_single_user(
    user: UserCreate, user_repo: UserRepository = Depends(get_user_repository)
):

    new_user = create_user(**user.model_dump(), user_repo=user_repo)
    return new_user


@router.put("/{id}")
async def update_entire_user(
    id: str, data: UserPut, user_repo: UserRepository = Depends(get_user_repository)
):

    updated_user = put_user(id, data, user_repo)
    return updated_user


@router.patch("/{id}")
async def update_user(
    id: str, data: UserPatch, user_repo: UserRepository = Depends(get_user_repository)
):

    patch_update_user = patch_users(id, data, user_repo)
    return patch_update_user


@router.delete("/{id}")
async def delete_user(
    id: str, user_repo: UserRepository = Depends(get_user_repository)
):

    return delete_users(id, user_repo)
