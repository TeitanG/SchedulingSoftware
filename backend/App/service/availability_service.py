from App.core import calculate_end_time
from App.db.models import daysOfTheWeek
from datetime import datetime
from App.core import validar_objectid,validate_entity_exist
from App.db import db_client
from fastapi import HTTPException, status
from App.db.schemas import availability_to_dict

def create_availability(provider_id : str,
                        business_id : str,
                        day : daysOfTheWeek,
                        start_time : datetime,
                        end_time : datetime,
                        duration : int,
                        active : bool,
                        capacity : int
                        ):
    
    appointment_end = calculate_end_time(start_hour= start_time, duration= duration)
    
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
    

    availabilities_db = {
        "provider_id" : provider_objectid,
        "business_id" : business_objectid,
        "day" : day.value,
        "start_time" : start_time,
        "end_time" : appointment_end,
        "duration" : duration,
        "active" : active,
        "capacity" : capacity
    }
    
    insert_id = db_client.availabilities.insert_one(availabilities_db).inserted_id
    new_available = db_client.availabilities.find_one({"_id": insert_id})
    return availability_to_dict(new_available)

    

