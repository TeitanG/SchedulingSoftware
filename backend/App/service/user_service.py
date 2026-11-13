from typing import Any

from fastapi import HTTPException, status
from pymongo import errors as pymongo_errors

from App.core import validar_objectid
from App.db.models import UserRole, Status
from App.db.schemas import UserPatch, UserPut, user_to_dict, users_to_dict
from App.repositories import UserRepository


def create_user(
    role: UserRole,
    username: str,
    name: str,
    business_id: str,
    email: str,
    user_status: Status,
    user_repo: UserRepository,
) -> dict[str, Any]:

    existing_username = user_repo.find_by_username(username)

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Error": "Username already exists"},
        )

    existing_email = user_repo.find_by_email(email)

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Error": "Email already exists"},
        )

    try:
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Business: {e!s}"},
        )

    user_data = {
        "role": role.value,
        "username": username,
        "name": name,
        "business_id": business_objectid,
        "email": email,
        "user_status": user_status.value,
    }

    try:
        user_id = user_repo.save(user_data)
    except pymongo_errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Error": "Usuario ya existe"},
        )
    except pymongo_errors.PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"Error": "Error al guardar el usuario"},
        )

    new_user = user_repo.find_by_id(user_id)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "User created but could not be retrieved"},
        )

    return user_to_dict(new_user)


def get_user_by_id(user_id: str, user_repo: UserRepository) -> dict[str, Any]:

    user = user_repo.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "User not found"}
        )

    return user_to_dict(user)


def get_all_users(user_repo: UserRepository) -> list[dict[str, Any]]:

    users = user_repo.find_all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "NOT FOUND"}
        )

    return users_to_dict(users)


def delete_users(user_id: str, user_repo: UserRepository):

    user = user_repo.delete(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "User not found"}
        )

    return {"User deleted"}


def patch_users(
    user_id: str, data: UserPatch, user_repo: UserRepository
) -> dict[str, Any]:

    try:
        user_objectid = validar_objectid(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    current_user = user_repo.find_by_id(str(user_objectid))

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Usuario no encontrado"},
        )

    updated_data = {
        clave: valor for clave, valor in data.model_dump().items() if valor is not None
    }

    if "name" in updated_data and not updated_data["name"].strip():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"ERROR": "Name cannot be empty"},
        )

    if "username" in updated_data and not updated_data["username"].strip():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"ERROR": "Username cannot be empty"},
        )

    sucess = user_repo.update(user_id, updated_data)

    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "User not updated"},
        )

    updated_user = user_repo.find_by_id(user_id)
    return {"message": "User updated successfully", "user": user_to_dict(updated_user)}


def put_user(user_id: str, data: UserPut, user_repo: UserRepository):

    current_user = user_repo.find_by_id(user_id)

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Usuario no encontrado"},
        )

    try:
        bussiness_objectid = validar_objectid(data.business_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": f"Business ID invalidao {e}"},
        )

    full_data: dict[str, Any] = {
        "role": data.role.value,
        "username": data.username,
        "name": data.name,
        "business_id": bussiness_objectid,
        "email": data.email,
        "user_status": data.user_status.value,
    }

    if data.username != current_user.get("username"):
        existing = user_repo.find_by_username(data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Username ya existe"},
            )

    if data.email != current_user.get("email"):
        existing = user_repo.find_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Email ya existe"},
            )

    sucess = user_repo.update(user_id, full_data)

    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "user not updated"}
        )

    updated_user = user_repo.find_by_id(user_id)

    return {"Mensaje": "Usuario actualizado", "usuario": user_to_dict(updated_user)}


def validar_provider(provider_id: str, user_repo: UserRepository):
    try:
        provider_objectid = validar_objectid(provider_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "ID de provider inválido"},
        )
    provider = user_repo.find_by_id(str(provider_objectid))

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Proovedor no encontrado"},
        )

    if provider["role"] != UserRole.provider:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"Error": "Usuario no es un provider"},
        )
