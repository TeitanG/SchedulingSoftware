from fastapi import HTTPException, status, Response
from App.db.models import BusinessType
from pydantic import EmailStr
from App.core import check_name,validar_email,normalize_phone, validar_objectid
from App.db import db_client
from App.db.schemas import business_to_dict, BusinessPatch, BussinessPut



def create_business(name : str,
                    business_type : BusinessType,
                    address : str,
                    email : EmailStr,
                    phone_number : str,
                    active: bool                    
                    ):
    
    list_db = list(db_client.businesses.find({}))
    
    try:
        check_name(value=name, existing_name=list_db, field= "business")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"error": str(e)})
    
    try:
        validar_email(email=email, existing_emails=list_db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error" : str(e)})
    
    phone_number_e164 = normalize_phone(phone= phone_number, region= "CO")
    
    businesses_db = {
        "name" : name,
        "business_type" : business_type.value,
        "address" : address,
        "email" : email,
        "phone_number" : phone_number_e164,
        "active" : active 
    }
    
    insert_id = db_client.businesses.insert_one(businesses_db).inserted_id
    new_business = db_client.businesses.find_one({"_id" : insert_id})
    return business_to_dict(new_business)

def search_business(field : str, key):
    if field =="_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : f"Id no encontrado{str(e)}"})
        
        business = db_client.businesses.find_one({field : key})

        if not business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"Error": "business not found"})
        
    return business


def delete_businesses(field: str, key):
    if field == "_id":
        try:
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={f"Error {str(e)}: Business not found"})

    deleted_buss = db_client.businesses.find_one_and_delete({field:key}) 

    if not deleted_buss:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"Error" : "Business not found/Deleted"})

    return Response(status_code=status.HTTP_200_OK)


def patch_business(business_id: str, data:BusinessPatch):

    try:
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= str(e))
    
    current_business = db_client.businesses.find_one({"_id": business_objectid})

    if not current_business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail= {"ERROR" : "Business not found"})

    updated_data = {
        k: v for k, v in data.model_dump().items() if v is not None
    }

    if "name" in updated_data and not updated_data["name"].strip():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                             detail= {"ERROR" : "Business name cannot be empty"})
    

    db_client.businesses.update_one(
        {"_id": business_objectid},
        {"$set":updated_data}
    )

    updated_business = db_client.businesses.find_one({"_id" : business_objectid})

    return{
        "message" : "Business updated successfully",
        "business": business_to_dict(updated_business)
    }

def put_bussiness(business_id: str, data:BussinessPut):

    try:
        business_objectid = validar_objectid(business_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_business = db_client.businesses.find_one({"_id" : business_objectid})

    if not current_business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"Error" : "Business no encontrado"})
    

    full_data={
        "name" : data.name,
        "business_type" : data.business_type.value,
        "address" : data.address,
        "email" : data.email,
        "phone_number": data.phone_number,
        "active" : data.active
    }

    try:
        check_name(value=full_data["name"], existing_name=current_business)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail= {"error": str(e)})
    
    try:
        validar_email(email=full_data["email"], existing_emails=current_business)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail={"error" : str(e)})
    
    phone_number_e164 = normalize_phone(phone= full_data["phone_number"], region= "CO")

    full_data.update({
        "phone_number" : phone_number_e164
    })

    db_client.businesses.update_many(
        {"_id": business_objectid},
        {"$set":full_data}
    )

    updated_business = db_client.businesses.find_one({"_id": business_objectid})

    return{
        "Message" :"Businesses updated",
        "Bussiness" : business_to_dict(updated_business)
    }

    

    




    
    


    



















    
    
   

    
    
    
