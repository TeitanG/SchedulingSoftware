from fastapi import APIRouter, status
from App.service import create_user, search_user, delete_users, patch_users
from App.db.schemas import UserCreate, user_to_dict, PatchUpdateUser
from App.db import db_client
from bson import ObjectId


router = APIRouter(
    prefix= "/users",
    tags=["usuarios"]
    )

@router.get("/")
async def get_users():
    return[user_to_dict(user) for user in db_client.users.find()]


@router.get("/{id}")
async def get_user_by_id(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_single_user(user : UserCreate):
    new_user= create_user(**user.model_dump())
    return new_user


@router.put("/{id}")
async def update_entire_user():
    pass

@router.patch("/{id}")
async def update_user(id: str, data:PatchUpdateUser):
    patch_update_user = patch_users(id, data)
    return patch_update_user


@router.delete("/{id}")
async def delete_user(id : str):
    return delete_users("_id", id)




