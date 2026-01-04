from App.db import db_client
from App.db.models import user_Type, user_Status
from App.core import validar_objectid, validate_entity_exist
from App.db.schemas import user_to_dict, PatchUpdateUser
from App.core import validar_username_email
from fastapi import HTTPException, status, Response


def create_user(role : user_Type,
                username : str,
                name : str,
                business_id: str,
                email: str,
                user_status : user_Status                
                ):
    
    existing_user = list(db_client.users.find({}))
    
    try:
        validar_username_email(email=email, username=username, existing_user=existing_user)
    except ValueError as e:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail={"error" : str(e)})    
        
    try:
        business_objectid = validar_objectid(business_id)
        validate_entity_exist(db_client.businesses, business_objectid, "Business")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"mensaje": f"Business: {str(e)}"})
    

    users_db = {
        "role" : role.value,
        "username" : username,
        "name" : name,
        "business_id" : business_objectid,
        "email" : email,
        "user_status" : user_status.value
    }

    insert_id = db_client.users.insert_one(users_db).inserted_id
    new_user = db_client.users.find_one({"_id" : insert_id})
    return user_to_dict(new_user)

def validar_provider(provider_id : str):
    provider_objectid = validar_objectid(provider_id)

    if not provider_objectid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" :"Id  no encontrado"})
    

    provider = db_client.users.find_one(
        {"_id", provider_objectid}
    )

    if not provider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" :"Proovedor no encontrado"})
    
    if provider["role"] != "Proveedor":
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail= {"Error" :"Usuario no es un proveedor"})
 

def search_user(field: str, key):
    if field == "_id":        
        try:        
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {f"Error{str(e)}" : "Not found"})
            
    user = db_client.users.find_one({field: key})
    if not user:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {f"Error" : "User not found"})

    return user_to_dict(user)  

def delete_users(field : str, key):
    if field == "_id":
        try:
            key= validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {f"Error{str(e)}" : "Not found"})
        
        user = db_client.users.find_one_and_delete({field: key})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {f"Error" : "User not found"})
        
    return Response(status_code=status.HTTP_200_OK)
        

def patch_users(user_id: str, data:PatchUpdateUser):

    try:
        user_objectid = validar_objectid(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    current_user = db_client.users.find_one("_id", user_objectid)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"Error": "Usuario no encontrado"})
    
    updated_data = {
        clave: valor for clave,valor in data.model_dump().items() if valor is not None
    }

    if "name" in updated_data and updated_data["name"].strip():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail={"ERROR": "Name cannot be empty"})
    
    if "username" in updated_data and updated_data["username"].strip():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail={"ERROR": "Username cannot be empty"}) 
    
    db_client.users.update_one(
        {"_id": user_objectid},
        {"$set": updated_data}
    )

    updated_user = db_client.users.find_one({"_id": user_objectid})

    return{
        "Message" : "User updated successfully",
        "User" : updated_user
    }

    


