from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class StatusAppointments(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "cancelado"

class Appointment(BaseModel):
    id : Optional[str] = None
    client_id : str
    provider_id : str
    service_id : str
    business_id: str
    start_time : datetime
    end_time: Optional[datetime] = None
    status_ : StatusAppointments
    notes : Optional[str]



    

   




    



