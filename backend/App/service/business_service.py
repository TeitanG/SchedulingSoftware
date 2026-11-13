from typing import Any

from fastapi import HTTPException, status
from pydantic import EmailStr

from App.core import normalize_phone
from App.db.models import BusinessType
from App.db.schemas import (
    BusinessPatch,
    BussinessPut,
    business_to_dict,
    businesses_to_dict,
)
from App.repositories import BusinessRepository


def create_business(
    name: str,
    business_type: BusinessType,
    address: str,
    email: EmailStr,
    phone_number: str,
    active: bool,
    business_repo: BusinessRepository,
) -> dict[str, Any]:

    if business_repo.find_by_name(name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Name is already registered"},
        )

    try:
        phone_number_e164 = normalize_phone(phone=phone_number, region="CO")

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "An error occurred saving your phone numbe"},
        )

    businesses_db = {
        "name": name,
        "business_type": business_type.value,
        "address": address,
        "email": email,
        "phone_number": phone_number_e164,
        "active": active,
    }

    business_id = business_repo.save(businesses_db)

    if not business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Business not save"},
        )

    new_business = business_repo.find_by_id(business_id)
    return business_to_dict(new_business)


def search_all_businesses(business_repo: BusinessRepository) -> list[dict[str, Any]]:
    businesses = business_repo.find_all()

    if not businesses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "No business found"}
        )

    return businesses_to_dict(businesses)


def search_business_by_id(id: str, business_repo: BusinessRepository):

    business = business_repo.find_by_id(id)

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Business not found"},
        )

    return business_to_dict(business)


def delete_businesses(id: str, business_repo: BusinessRepository):
    deleted_business = business_repo.delete(id)
    if not deleted_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Business not found"},
        )
    return {"Mensaje": "Business deleted"}


def patch_business(
    business_id: str, data: BusinessPatch, business_repo: BusinessRepository
) -> dict[str, Any]:

    current_business = business_repo.find_by_id(business_id)

    if not current_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"ERROR": "Business not found"},
        )

    updated_data = {
        clave: valor for clave, valor in data.model_dump().items() if valor is not None
    }

    if "name" in updated_data and not updated_data["name"].strip():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"ERROR": "Business name cannot be empty"},
        )

    business = business_repo.update(business_id, updated_data)

    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business not updated"},
        )

    updated_business = business_repo.find_by_id(business_id)

    return {
        "message": "Business updated successfully",
        "business": business_to_dict(updated_business),
    }


def put_business(
    business_id: str, data: BussinessPut, business_Repo: BusinessRepository
) -> dict[str, Any]:

    current_business = business_Repo.find_by_id(business_id)

    if not current_business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Business no encontrado"},
        )

    full_data = {
        "name": data.name,
        "business_type": data.business_type.value,
        "address": data.address,
        "email": data.email,
        "phone_number": data.phone_number,
        "active": data.active,
    }

    if data.name != current_business.get("name"):
        existing = business_Repo.find_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Nombre ya existe"},
            )
    if data.email != current_business.get("email"):
        existing = business_Repo.find_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"Error": "Email ya existe"},
            )

    try:
        phone_number_e164 = normalize_phone(
            phone=full_data["phone_number"], region="CO"
        )

        full_data.update({"phone_number": phone_number_e164})

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "An error occured while saving the phone number"},
        )

    sucess = business_Repo.update(business_id, full_data)

    if not sucess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Business not updated"},
        )

    updated_business = business_Repo.find_by_id(business_id)

    return {
        "Message": "Businesses updated",
        "Bussiness": business_to_dict(updated_business),
    }
