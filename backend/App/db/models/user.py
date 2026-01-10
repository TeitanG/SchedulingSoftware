from typing import Optional
from pydantic import BaseModel
from enum import Enum

class user_Type(str, Enum):
    Admin = "Admin"
    client = "client"
    provider = "provider"

class user_Status(str, Enum):
    active = "active"
    inactive = "inactive"


class users(BaseModel):
    id: Optional[str] = None
    role : user_Type
    username : str
    name : str
    business_id: Optional[str] = None
    email : str
    user_status : user_Status






