from fastapi import APIRouter, status
from App.service import create_user, search_user
from App.db.schemas.user_schema import UserCreate, UserSchema
from App.db.client import db_client
from bson import ObjectId


router = APIRouter(
    prefix= "/users",
    tags=["usuarios"]
    )

@router.get("/get_users")
async def get_users():
    return[UserSchema(user) for user in db_client.users.find()]


@router.get("/user/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/create_user", status_code= status.HTTP_201_CREATED)
async def single_user(user : UserCreate):
    new_user= create_user(**user.model_dump())
    return new_user


