from fastapi import HTTPException, status, Response
from bson import ObjectId
from typing import Dict, Any
from datetime import datetime
from App.db import db_client
from App.db.schemas import service_to_dict, ServicePatch, ServicePut
from App.core import validar_objectid, validate_entity_exist
from App.core import check_name
from App.repositories import ServiceRepository, BusinessRepository, UserRepository


def create_services(
        name : str,
        description : str,
        price : int,        
        provider_id : str,
        business_id : str,
        duration : int,
        capacity : int,
        service_repo : ServiceRepository,
        business_repo: BusinessRepository,
        user_repo: UserRepository        
        )-> Dict[str, Any]:
    
    
    existing_service = service_repo.find_by_name(name)
    if existing_service:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail= {"Error": f"Service with name '{name}' Already exists"})
    
    provider = user_repo.find_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"Error" : f"Provider id: '{provider_id}' not found"})        

    business = business_repo.find_by_id(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error": f"business id : '{business_id}' not found"})    
    
          
    service_data = {
        "name" : name,
        "description" : description,
        "price" : price,
        "provider" : ObjectId(provider_id),
        "business_id" : ObjectId(business_id),
        "duration" : duration,
        "capacity" : capacity,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    service_id = service_repo.save(service_data)

    new_service = service_repo.find_by_id(service_id)

    if not new_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= {"Service Created but could not be retrieved"})

    return service_to_dict(new_service)
    
def search_all_services(service_repo : ServiceRepository)-> Dict[str,Any]:
    
    services = service_repo.find_all()

    if not services:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= {"Error" : "No services found"})
    
    return service_to_dict(services)


def search_service_by_id(service_id: str, 
                         service_repo: ServiceRepository)->Dict[str,Any]:
    service = service_repo.find_by_id(service_id)

    if not service:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail={"error":"service not found"})
    return service_to_dict(service)
    

def delete_services(service_id: str,
                    service_repo: ServiceRepository)->bool:
    
    deleted_service = service_repo.delete(service_id)

    if not deleted_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error": "Servicio no encontrado"})
    
    return True    


def patch_services(service_id:str, data:ServicePatch,
                   service_repo: ServiceRepository) -> Dict[str, Any]:
    
    
    current_service= service_repo.find_by_id(service_id)

    if not current_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"Error": "Servicio no encontrado"})
    
    update_data= {
        clave: valor for clave,valor in data.model_dump().items() if valor is not None
    }

    if "name" in update_data and not update_data["name"].strip():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail={"ERROR": "Name cannot be empty"})
    
    sucess =  service_repo.update(service_id, update_data)

    if not sucess:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"Service not updated"})

    updated_service =service_repo.find_by_id(service_id)

    return{
        "Message" : "Service updated successfully",
        "Service" :  service_to_dict(updated_service)
    }


def put_service(service_id: str, data:ServicePut, 
                service_repo : ServiceRepository):

    existing_names = service_repo.find_all()

   
    

    current_service = service_repo.find_by_id(service_id)

    if not current_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "Service Not found"})
    

    full_data = {
        "name" : data.name,
        "description" : data.description,
        "price" : data.price,
        "provider_id":data.provider_id,
        "business_id": data.business_id,
        "duration" : data.duration,
        "capacity": data.capacity,
        "created_at": data.created_at,
        "updated_at": datetime.now
    }

    provider_id = full_data["provider_id"]
    business_id = full_data["business_id"]

    try:
        provider_objectid = validar_objectid(provider_id)        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"mensaje" : f"Provider : {str(e)}" })
        
    try:
        business_objectid = validar_objectid(business_id)        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"mensaje" : f"Business : {str(e)}" })
    
    if not check_name(full_data["name"], existing_names):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"Error" : "Nombre ya existe"})
    
    full_data.update({
        "provider_id": provider_objectid,
        "business_id" : business_objectid
    })

    sucess = service_repo.update(service_id, full_data)

    if not sucess:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"Error": "User not updated"})

    updated_service = service_repo.find_by_id(service_id)

    return{
        "Message" : "Servicio actualizado",
        "Servicio" : service_to_dict(updated_service)
    }
