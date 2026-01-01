from fastapi import HTTPException, status, Response
from App.db.models.business import BusinessType
from pydantic import EmailStr
from App.core.service_core import check_name
from App.core.users_core import validar_email
from App.core.business_core import normalize_phone
from App.db.client import db_client
from App.db.schemas.business_schemas import business_to_dict
from App.core import validar_objectid



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










    
    
   

    
    
    
