from App.db import db_client
from bson import ObjectId
from App.db.models.user import user_Type, user_Status
from App.core.appointments_core import validar_objectid, validate_entity_exist
from App.db.schemas import UserSchema
from App.core.users_core import validar_username_email
from fastapi import HTTPException, status


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
    
    business_objectid = None
    if business_objectid:
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
    return UserSchema(new_user)


def search_user(field: str, key):
    if field == "_id":        
        try:        
            key = validar_objectid(key)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= {"Error" : "Not found"})
            
    user = db_client.users.find_one({field: key})
    if not user:  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= {"Error" : "User not found"})

    return UserSchema(user)          
        
        



    

    

    


    

    
        


    



