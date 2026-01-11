from fastapi import (APIRouter, status,
                    Depends)
from typing import Dict, Any, List
from bson import ObjectId

from App.service import (create_user, get_all_users,
                        delete_users, patch_users,
                        put_user, get_user_by_id)
from App.db.schemas import (UserCreate, user_to_dict, 
                            UserPatch, UserPut)
from App.db import db_client
from App.dependencies import (get_user_repository)
from App.repositories import UserRepository

router = APIRouter(
    prefix= "/users",
    tags=["usuarios"]
    )

@router.get("/")
async def get_users(
    user_repo: UserRepository = Depends(get_user_repository)   
    ):

    return get_all_users(user_repo)
    
@router.get("/{id}")
async def get_user(id: str,
                   user_repo: UserRepository = Depends(get_user_repository)):

    return get_user_by_id(id, user_repo)

@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_single_user(user : UserCreate):

    new_user= create_user(**user.model_dump())
    return new_user


@router.put("/{id}")
async def update_entire_user(id: str,
                            data : UserPut,
                            user_repo: UserRepository = Depends(get_user_repository)):
    
    updated_user = put_user(id, data, user_repo)
    return updated_user

@router.patch("/{id}")
async def update_user(id: str,
                    data:UserPatch,
                    user_repo: UserRepository= Depends(get_user_repository)):
    
    patch_update_user = patch_users(id, data, user_repo)
    return patch_update_user


@router.delete("/{id}")
async def delete_user(id : str, user_repo: UserRepository = Depends(get_user_repository)):

    return delete_users(id, user_repo)




