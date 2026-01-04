from App.db import db_client
from App.db.schemas import service_to_dict, ServicePatch, ServicePut
from App.core import validar_objectid, validate_entity_exist
from fastapi import HTTPException, status, Response
from App.core import check_name


def create_services(
        name : str,
        description : str,
        price : int,        
        provider_id : str,
        business_id : str,
        duration : int,
        capacidad : int
        ):
    
    existing_names = list(db_client.services.find({}))

    try:
        check_name(value= name, existing_name=existing_names)
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
        "business_id" : business_objectid,
        "duration" : duration,
        "capacidad" : capacidad
    }

    insert_id = db_client.services.insert_one(services_db).inserted_id
    new_service = db_client.services.find_one({"_id":insert_id})

    return service_to_dict(new_service)


def search_service(field: str , key):
    if field == "_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
        
    service = db_client.services.find_one({field: key})
    if not service:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
    
    return service_to_dict(service)


def delete_services(field : str, key):
    if field == "_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
        
    service = db_client.services.find_one_and_delete({field: key})

    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
    
    return Response(status_code=status.HTTP_200_OK)


def patch_services(service_id:str, data:ServicePatch):

    try:
        service_objectid = validar_objectid(service_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_service= db_client.services.find_one({"_id": service_objectid})

    if not current_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"Error": "Servicio no encontrado"})
    
    update_data= {
        k: v for k,v in data.model_dump().items() if v is not None
    }

    if "name" in update_data and not update_data["name"].strip():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail={"ERROR": "Name cannot be empty"})
    
    db_client.services.update_one(
        {"_id": service_objectid},
        {"$set":update_data}
    )

    updated_service = db_client.services.find_one({"_id": service_objectid})

    return{
        "Message" : "Service updated successfully",
        "Service" :  service_to_dict(updated_service)
    }


def put_service(service_id: str, data:ServicePut):

    existing_names = list(db_client.services.find({}))

    try:
        service_objectid= validar_objectid(service_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail= str(e))
    

    current_service = db_client.services.find_one({"_id": service_objectid})

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
        "capacidad": data.capacidad
    }

    provider_id = full_data["provider_id"]
    business_id = full_data["business_id"]

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
    
    if not check_name(full_data["name"], existing_names):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"Error" : "Nombre ya existe"})
    
    full_data.update({
        "provider_id": provider_objectid,
        "business_id" : business_objectid
    })

    db_client.services.update_one(
        {"_id": service_objectid},
        {"$set": full_data}
    )

    updated_service = db_client.services.find_one({"_id": service_objectid})

    return{
        "Message" : "Servicio actualizado",
        "Servicio" : service_to_dict(updated_service)
    }
