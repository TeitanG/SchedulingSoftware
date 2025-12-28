from fastapi import APIRouter, status
from App.service.service_service import create_services
from App.db.schemas.service_schemas import serviceCreate, service_to_dict
from App.db.client import db_client


router = APIRouter(
    prefix= "/services",
    tags=["service"]
)

@router.post("/")
async def create_service(service : serviceCreate):
    new_service = create_services(**service.model_dump())
    return new_service

@router.get("/")
async def get_service():
    return [service_to_dict(service) for service in db_client.services.find()]
    
