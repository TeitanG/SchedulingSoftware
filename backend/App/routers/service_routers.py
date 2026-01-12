from fastapi import APIRouter, status, Depends
from bson import ObjectId
from App.service import (create_services, search_service_by_id,
                         delete_services, patch_services,
                         put_service, search_all_services)
from App.db.schemas import (ServiceCreate, service_to_dict,
                             ServicePatch, ServicePut)
from App.dependencies import get_service_repository
from App.repositories import ServiceRepository
from App.db import db_client




router = APIRouter(
    prefix= "/services",
    tags=["service"]
)

@router.get("/")
async def get_services(
    service_repo : ServiceRepository = Depends(get_service_repository)
    ):
    return search_all_services(service_repo)

@router.get("/{id}")
async def get_service_by_id(id: str, 
                            service_repo: ServiceRepository = Depends(get_service_repository)):
    return search_service_by_id(id, service_repo)

@router.post("/")
async def create_service(service : ServiceCreate,
                         service_repo: ServiceRepository = Depends(get_service_repository)):                                                
    new_service = create_services(**service.model_dump(),
                                  service_repo=service_repo)
    return new_service


@router.put("/{id}")
async def update_entire_service(id: str, data: ServicePut,
                                service_repo : ServiceRepository = Depends(get_service_repository)):
    updated_service = put_service(id, data, service_repo)
    return updated_service

@router.patch("/{id}")
async def update_service(id : str, data: ServicePatch,
                         service_repo : ServiceRepository = Depends(get_service_repository)):
    updated_service = patch_services(id, data,service_repo)
    return updated_service
    

@router.delete("/{id}")
async def delete_Service(id:str,
                         service_repo : ServiceRepository = Depends(get_service_repository)):
    return delete_services(id, service_repo)






    
