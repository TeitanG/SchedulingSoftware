from App.db.models.user import user_Type, user_Status
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel): 

    role: user_Type
    username : str
    name : str
    business_id: str | None = None
    email : EmailStr
    user_status : user_Status
    

def UserSchema(user)-> dict:
   return{
    "id": str(user["_id"]),  
    "role": user["role"].value if hasattr(user["role"],"value")else user["role"],  
    "username": user["username"],
    "name": user["name"],
    "business_id": (
            str(user["business_id"])
            if user.get("business_id") is not None
            else None),
    "email": user["email"],  
    "user_status" : user["user_status"].value if hasattr(user["user_status"],"value")else user["user_status"],  
   }
    
    



