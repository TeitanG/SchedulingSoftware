from fastapi import APIRouter, status
from App.service import create_user, search_user
from App.db.schemas.user_schema import UserCreate, user_to_dict
from App.db.client import db_client
from bson import ObjectId


router = APIRouter(
    prefix= "/users",
    tags=["usuarios"]
    )

@router.get("/")
async def get_users():
    return[user_to_dict(user) for user in db_client.users.find()]


@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_single_user(user : UserCreate):
    new_user= create_user(**user.model_dump())
    return new_user


