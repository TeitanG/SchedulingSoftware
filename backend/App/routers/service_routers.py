from fastapi import APIRouter, status
from App.service.service_service import create_services
from App.db.schemas.service_schemas import ServiceCreate, service_to_dict
from App.db.client import db_client


router = APIRouter(
    prefix= "/services",
    tags=["service"]
)




@router.get("/")
async def get_services():
    return [service_to_dict(service) for service in db_client.services.find()]

@router.get("/{id}")
async def get_service_by_id(id: str):
    pass

@router.post("/")
async def create_service(service : ServiceCreate):
    new_service = create_services(**service.model_dump())
    return new_service


@router.put("/")
async def update_entire_service():
    pass

@router.patch("/")
async def update_service():
    pass


@router.delete("/")
async def delete_Service():
    pass






    
