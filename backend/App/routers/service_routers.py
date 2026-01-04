from fastapi import APIRouter, status
from App.service import create_services, search_service, delete_services, patch_services
from App.db.schemas import ServiceCreate, service_to_dict, PatchUpdateService
from App.db import db_client
from bson import ObjectId



router = APIRouter(
    prefix= "/services",
    tags=["service"]
)

@router.get("/")
async def get_services():
    return [service_to_dict(service) for service in db_client.services.find()]

@router.get("/{id}")
async def get_service_by_id(id: str):
    return search_service("_id", ObjectId(id))

@router.post("/")
async def create_service(service : ServiceCreate):
    new_service = create_services(**service.model_dump())
    return new_service


@router.put("/")
async def update_entire_service():
    pass

@router.patch("/{id}")
async def update_service(id : str, data: PatchUpdateService):
    updated_service = patch_services(id, data)
    return updated_service
    

@router.delete("/{id}")
async def delete_Service(id:str):
    return delete_services("_id", id)






    
