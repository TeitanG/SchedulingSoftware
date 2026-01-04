from App.core import calculate_end_time
from App.db.models import daysOfTheWeek
from datetime import datetime
from App.core import validar_objectid,validate_entity_exist
from App.db import db_client
from fastapi import HTTPException, status, Response
from App.db.schemas import availability_to_dict, PatchUpdateAvailability



############# CREATE AVAILABILITY #############
def create_availability(provider_id : str,
                        business_id : str,
                        day : daysOfTheWeek,
                        start_time : datetime,
                        end_time : datetime,
                        active : bool                        
                        ):    
   
    
    try: 
        provider_objectid = validar_objectid(provider_id)
        validate_entity_exist(db_client.availabilities, provider_id, "Proveedor")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Mensaje" : f"Proveedor {str(e)}"})
    
    try: 
        business_objectid = validar_objectid(business_id)
        validate_entity_exist(db_client.availabilities, business_id, "Business")
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
    
    insert_id = db_client.availabilities.insert_one(availabilities_db).inserted_id
    new_available = db_client.availabilities.find_one({"_id": insert_id})
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


############# SEARCH AVAILABILITY #############
def search_availability(field: str, key):
    if field == "_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
        
    availability = db_client.availabilities.find_one({field: key})
    if not availability:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" : "availability not found"})

    return availability_to_dict(availability)  


############# DELETE AVAILABILITY #############
def delete_availability(field: str, key):
    if field == "_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "Id not found"})
        
    availability = db_client.availabilities.find_one_and_delete({field : key})
    if not availability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error" : "availability not found"})
    
    return Response(status_code=status.HTTP_202_ACCEPTED)


############# PUT AVAILABILITY #############
def patch_availability(availability_id : str, data: PatchUpdateAvailability):
    try:
        availability_objectid = validar_objectid(availability_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_availability = db_client.availabilities.find_one(
        {"_id": availability_objectid}        
    )

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
    

    provider = db_client.users.find_one({"_id" : provider_objectid})
    business = db_client.businesses.find_one({"_id": business_objectid})


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
    
    existing = db_client.availabilities.find_one({
        "_id": {"$ne": availability_objectid},
        "provider_id": provider_objectid,
        "business_id": business_objectid,
        "day": day,
        "$or": [
            {
                "start_time": {"$lt": end_time},
                "end_time": {"$gt": start_time}
            }
        ]
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail={"Error" : "Availability overlaps with an existing one"})
    
    db_client.availabilities.update_one(
        {"_id": availability_objectid},
        {"$set": updated_data}
    )

    updated_availability = db_client.availabilities.find_one("_id", availability_objectid)

    return {
        "mensaje" : "Availability updated successfully",
        "Availability" : updated_availability  
    }    
 

    
