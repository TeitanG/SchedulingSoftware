from bson.errors import InvalidId
from fastapi import HTTPException, Response, status

from App.core import time_from_db, time_to_db, validar_objectid
from App.db.schemas import (
    AvailabilityCreate,
    AvailabilityPatch,
    PutAvailability,
    availabilities_to_dict,
    availability_to_dict,
)
from App.repositories import AvailabilityRepository, BusinessRepository, UserRepository


def create_availability(
    data: AvailabilityCreate, availability_repo: AvailabilityRepository
):

    try:
        provider_objectid = validar_objectid(data.provider_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Mensaje": f"Proveedor {e!s}"},
        )

    try:
        business_objectid = validar_objectid(data.business_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Mensaje": f"Business {e!s}"},
        )

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "start_time must be before end_time"},
        )

    availabilities_db = {
        "provider_id": provider_objectid,
        "business_id": business_objectid,
        "day": data.day.value,
        "start_time": time_to_db(data.start_time),
        "end_time": time_to_db(data.end_time),
        "active": data.active,
    }

    availability_id = availability_repo.save(availabilities_db)

    if not availability_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Availability not saved"},
        )

    new_available = availability_repo.find_by_id(availability_id)
    if not new_available:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Availability not found"},
        )

    return availability_to_dict(new_available)


def validar_provider_business_ids(
    provider_id: str,
    business_id: str,
):
    try:
        business_objectid = validar_objectid(business_id)
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Business: {e!s}"},
        )
    try:
        provider_objectid = validar_objectid(provider_id)
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"mensaje": f"Proveedor: {e!s}"},
        )

    return business_objectid, provider_objectid


def get_availabilties(availability_repo: AvailabilityRepository):
    availabilities = availability_repo.find_all()

    if not availabilities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "No availabilities found"},
        )
    return availabilities_to_dict(availabilities)


def get_availability(id: str, availability_repo: AvailabilityRepository):
    availability = availability_repo.find_by_id(id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "availability not found"},
        )

    return availability_to_dict(availability)


def delete_availability(id: str, availability_repo: AvailabilityRepository):

    availability = availability_repo.delete(id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "availability not found"},
        )

    return Response(status_code=status.HTTP_200_OK)


def patch_availability(
    availability_id: str,
    data: AvailabilityPatch,
    availability_repo: AvailabilityRepository,
    user_repo: UserRepository,
    business_repo: BusinessRepository,
):

    current_availability = availability_repo.find_by_id(availability_id)

    if not current_availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Availability not found"},
        )

    updated_data = {
        clave: valor for clave, valor in data.model_dump().items() if valor is not None
    }

    business_objectid, provider_objectid = validar_provider_business_ids(
        provider_id=updated_data.get(
            "provider_id", current_availability["provider_id"]
        ),
        business_id=updated_data.get(
            "business_id", current_availability["business_id"]
        ),
    )

    updated_data.update(
        {"provider_id": provider_objectid, "business_id": business_objectid}
    )

    provider = user_repo.find_by_id(str(provider_objectid))
    business = business_repo.find_by_id(str(business_objectid))

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Provider not found"},
        )
    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Business not found"},
        )

    start_time = updated_data.get("start_time") or time_from_db(
        current_availability["start_time"]
    )
    end_time = updated_data.get("end_time") or time_from_db(
        current_availability["end_time"]
    )

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "start_time must be before end_time"},
        )

    day = updated_data.get("day", current_availability["day"])

    updated_data["start_time"] = time_to_db(start_time)
    updated_data["end_time"] = time_to_db(end_time)

    overlapping = availability_repo.find_overlapping_availability(
        availability_id,
        str(provider_objectid),
        str(business_objectid),
        day,
        updated_data["start_time"],
        updated_data["end_time"],
    )

    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Error": "Availability overlaps with an existing one"},
        )

    update = availability_repo.update(availability_id, updated_data)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Availability not updated"},
        )

    updated_availability = availability_repo.find_by_id(availability_id)

    if not updated_availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "Updated availability not found"},
        )

    return {
        "mensaje": "Availability updated successfully",
        "Availability": availability_to_dict(updated_availability),
    }


def put_availability(
    availability_id: str,
    data: PutAvailability,
    availability_repo: AvailabilityRepository,
):
    try:
        availability_objectid = validar_objectid(availability_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    business_objectid, provider_objectid = validar_provider_business_ids(
        provider_id=data.provider_id, business_id=data.business_id
    )

    current_availability = availability_repo.find_by_id(str(availability_objectid))

    if not current_availability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"Error": "Horario no encontrado"},
        )

    start_time = time_to_db(data.start_time)
    end_time = time_to_db(data.end_time)

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "Error": "La hora de inicio no puede ser"
                "mayor que la hora de finalizacion"
            },
        )

    full_data = {
        "provider_id": str(provider_objectid),
        "business_id": str(business_objectid),
        "day": data.day.value,
        "start_time": start_time,
        "end_time": end_time,
        "active": data.active,
    }

    full_data.update(
        {
            "provider_id": str(provider_objectid),
            "business_id": str(business_objectid),
        }
    )

    day = full_data["day"]

    overlaping = availability_repo.find_overlapping_availability(
        availability_id,
        str(provider_objectid),
        str(business_objectid),
        day,
        start_time,
        end_time,
    )

    if overlaping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"Error": "Availability overlaps with an existing one "},
        )

    updated_data = availability_repo.update(availability_id, full_data)

    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"Error": "No se pudo actualizar"},
        )

    updated_availability = availability_repo.find_by_id(str(availability_objectid))

    return {
        "Message": "Cita Actualizada",
        "updated": availability_to_dict(updated_availability),
    }
