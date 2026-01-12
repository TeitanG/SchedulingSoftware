from fastapi import HTTPException, status, Response
from datetime import datetime
from typing import List, Dict, Optional
from App.core import calculate_end_time
from App.db.models import daysOfTheWeek
from App.core import validar_objectid,validate_entity_exist
from App.db import db_client
from App.db.schemas import availability_to_dict, AvailabilityPatch, PutAvailability
from App.repositories import AvailabilityRepository, UserRepository, BusinessRepository


def create_availability(provider_id : str,
                        business_id : str,
                        day : daysOfTheWeek,
                        start_time : datetime,
                        end_time : datetime,
                        active : bool,
                        availability_repo : AvailabilityRepository,
                        user_repo : UserRepository,
                        business_repo : BusinessRepository
                        ):    
   
    
    try: 
        provider_objectid = validar_objectid(provider_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Mensaje" : f"Proveedor {str(e)}"})
    
    try: 
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Mensaje" : f"Business {str(e)}"})
    
    if start_time >= end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "start_time must be before end_time"})
    

    availabilities_db = {
        "provider_id" : provider_objectid,
        "business_id" : business_objectid,
        "day" : day.value,
        "start_time" : start_time,
        "end_time" : end_time,        
        "active" : active,
    }
    
    availability_id = availability_repo.save(availabilities_db)

    if not availability_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"error" : "Availability not saved"})
    
    new_available = availability_repo.find_by_id(availability_id)
    if not new_available:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "Availability not found"})
    
    return availability_to_dict(new_available)


def validar_provider_business_ids(provider_id: str,
                                  business_id: str,
                                  ):
    try:
        business_objectid = validar_objectid(business_id)
        validate_entity_exist(db_client.businesses, business_objectid, "Business")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"mensaje": f"Business: {str(e)}"})
    
    try:
        provider_objectid = validar_objectid(provider_id)
        validate_entity_exist(db_client.users, provider_objectid, "Proveedor", filters={"role":"Proveedor"})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Proveedor: {str(e)}"})
     
    return business_objectid, provider_objectid


def search_availabilities(availability_repo : AvailabilityRepository):
    return availability_repo.find_all()


def search_availability(id : str, availability_repo: AvailabilityRepository):
    availability = availability_repo.find_by_id(id)
    if not availability:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" : "availability not found"})

    return availability_to_dict(availability)  


def delete_availability(id: str, 
                        availability_repo : AvailabilityRepository):

    availability = availability_repo.delete(id)
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error" : "availability not found"})
    
    return Response(status_code=status.HTTP_200_OK)


def patch_availability(availability_id : str, data: AvailabilityPatch,
                       availability_repo : AvailabilityRepository,
                       user_repo : UserRepository,
                       business_repo : BusinessRepository):
    try:
        availability_objectid = validar_objectid(availability_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_availability = availability_repo.find_by_id(availability_id)

    if not current_availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= {"Error": "Availability not found"})
    
    updated_data = {        
        k: v for k, v in data.model_dump().items() if v is not None
    }
   

    business_objectid, provider_objectid = (
        validar_provider_business_ids(
            provider_id=updated_data["provider_id"],
            business_id=updated_data["business_id"]
        )
    )
    
    updated_data.update({
        "provider_id": provider_objectid,
        "business_id" : business_objectid         
    })
    

    provider =user_repo.find_by_id(str(provider_objectid))
    business =business_repo.find_by_id(str(business_objectid))


    if not provider:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail={"Error" : "Provider not found"}
        )
    if not business:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail={"Error" : "Business not found"}
        )
    
    start_time = updated_data.get("start_time", current_availability["start_time"])
    end_time = updated_data.get("end_time", current_availability["end_time"])

    
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "start_time must be before end_time" }
        )
    
    day = updated_data.get("day", current_availability["day"])   



    overlapping = availability_repo.find_overlapping_availability(availability_id,
                                                                str(provider_objectid),
                                                                str(business_objectid),
                                                                day,
                                                                start_time,
                                                                end_time)
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"Error" : "Availability overlaps with an existing one"})
    
    update = availability_repo.update(availability_id, updated_data)

    if not update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"Error" : "Availability not found"})

    updated_availability = availability_repo.find_by_id(availability_id)

    return {
        "mensaje" : "Availability updated successfully",
        "Availability" : updated_availability  
    }    
 

def put_availability(availability_id:str, data:PutAvailability,
                     availability_repo: AvailabilityRepository):
    try: 
        availability_objectid = validar_objectid(availability_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_availability = availability_repo.find_by_id(availability_id)

    if not current_availability:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"Error" : "Horario no encontrado"})
    

    full_data = {
        "provider_id": data.provider_id,
        "business_id": data.business_id,
        "day": data.day.value,
        "start_time": data.start_time,
        "end_time": data.end_time,
        "active": data.active
    }
    if full_data["start_time"] >= full_data["end_time"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"Error" : "La hora de inicio no puede ser"
                            "mayor que la hora de finalizacion"})
    
    

    provider_id, business_id = validar_provider_business_ids(
        provider_id=full_data["provider_id"],
        business_id=full_data["business_id"]
    )

    full_data.update({
        "provider_id": provider_id,
        "business_id": business_id,        
    })

    updated_data = availability_repo.update(availability_id, full_data)

    updated_availability = db_client.availabilities.find_one({"_id": availability_objectid})

    return{
        "Message" : "Cita Actualizada",
        "updated" : availability_to_dict(updated_availability)
    }



   

    
    


    
