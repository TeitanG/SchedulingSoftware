from typing import Optional
from pydantic import BaseModel

class service(BaseModel):
    id : Optional[str] = None
    name : str
    description : Optional[str] = None
    price : Optional[int] = None    
    provider_id : str
    business_id : str
    duration : int
    capacity : int

    