from fastapi import APIRouter
from App.service import create_availability
from App.db.schemas import CreateAvailability, availability_to_dict
from App.db import db_client


router = APIRouter(
    prefix= "/availabilities",
    tags=["availabilities"]
)

@router.get("/")
async def get_availabilities():
    return[availability_to_dict(availability) for availability in db_client.availabilities.find()]



@router.get("/{id}")
async def get_one_availability(id: str):
    pass

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
async def delete_availability():
    pass
