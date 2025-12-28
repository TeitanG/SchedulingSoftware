from fastapi import APIRouter, status
from App.service.service_service import create_services
from App.db.schemas.service_schemas import serviceCreate, serviceSchema
from App.db.client import db_client


router = APIRouter(
    prefix= "/service",
    tags=["service"]
)

@router.post("/create_service")
async def create_service(service : serviceCreate):
    new_service = create_services(**service.model_dump())
    return new_service

@router.get("/get_services")
async def get_service():
    return [serviceSchema(service) for service in db_client.services.find()]
    
