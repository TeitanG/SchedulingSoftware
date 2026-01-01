from fastapi import APIRouter
from App.service import create_availability, search_availability, delete_availability
from App.db.schemas import CreateAvailability, availability_to_dict
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
async def create_availabilities(availability : CreateAvailability):
    new_availability = create_availability(**availability.model_dump())
    return new_availability
    

@router.put("/{id}")
async def update_entire_availability():
    pass

@router.patch("/{id}")
async def update_availability():
    pass

@router.delete("/{id}")
async def deleted_availability(id : str):
    return delete_availability("_id", id)
