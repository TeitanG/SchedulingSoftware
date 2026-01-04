from fastapi import APIRouter
from App.service import (create_availability, search_availability,
                          delete_availability, patch_availability,
                          put_availability)
from App.db.schemas import (AvailabilityCreate, availability_to_dict,
                             AvailabilityPatch, PutAvailability)
from App.db import db_client
from bson import ObjectId


router = APIRouter(
    prefix= "/availabilities",
    tags=["availabilities"]
)

@router.get("/")
async def get_availabilities():
    return[availability_to_dict(availability) for availability in db_client.availabilities.find()]



@router.get("/{id}")
async def get_one_availability(id: str):
    return search_availability("_id", ObjectId(id))

@router.post("/")
async def create_availabilities(availability : AvailabilityCreate):
    new_availability = create_availability(**availability.model_dump())
    return new_availability
    

@router.put("/{id}")
async def update_entire_availability(id: str, PutAvailability):
    updated_availability = put_availability(id, PutAvailability)
    

@router.patch("/{id}")
async def update_availability(id: str, availability :AvailabilityPatch):
    updated_availability = patch_availability(id, availability)
    return updated_availability

@router.delete("/{id}")
async def deleted_availability(id : str):
    return delete_availability("_id", id)
