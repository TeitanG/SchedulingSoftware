from App.db.client import db_client
from App.db.schemas import service_to_dict
from App.core.appointments_core import validar_objectid, validate_entity_exist
from fastapi import HTTPException, status
from App.core.service_core import check_name


def create_services(
        name : str,
        description : str,
        price : int,        
        provider_id : str,
        business_id : str
        ):
    existing_names = list(db_client.services.find({}))

    try:
        check_name(name= name, existing_name=existing_names)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error" : str(e)})
        
    provider_objectid = None
    business_objectid = None        

    try:
        provider_objectid = validar_objectid(provider_id)
        validate_entity_exist(db_client.services, provider_objectid, "Provider")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail={"mensaje" : f"Provider : {str(e)}" })
    
    try:
        business_objectid = validar_objectid(business_id)
        validate_entity_exist(db_client.services, business_objectid, "Business")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail={"mensaje" : f"Business : {str(e)}" })
          
    services_db = {
        "name" : name,
        "description" : description,
        "price" : price,
        "provider" : provider_objectid,
        "business_id" : business_objectid
    }

    insert_id = db_client.services.insert_one(services_db).inserted_id
    new_service = db_client.services.find_one({"_id":insert_id})

    return service_to_dict(new_service)
