from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum




class BusinessType(str, Enum):
    medical = "medical"
    beauty =  "beauty"
    logistics = "logistics"
    custom = "custom"





class Business(BaseModel):
    id : Optional[str] = None
    name : str
    business_type : BusinessType
    address : Optional[str] = None
    email : EmailStr
    phone_number : str
    active : bool
    