from typing import Optional
from pydantic import BaseModel
from enum import Enum



class businessType(str, Enum):
    medical = "medical"
    beauty =  "Belleza"
    logistics = "logistica"
    custom = "etc"





class business(BaseModel):
    id : Optional[str] = None
    name : str
    business_type : str
    address : Optional[str] = None
    contact_info : str
    active : bool
    