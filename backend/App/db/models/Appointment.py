from typing import Optional
from pydantic import BaseModel
from datetime import datetime, time
from enum import Enum

class StatusAppointments(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "canceled"

class Appointment(BaseModel):
    id : Optional[str] = None
    client_id : str
    provider_id : str
    service_id : str
    business_id: str
    start_time : datetime
    end_time: Optional[datetime] = None
    status : StatusAppointments
    notes : Optional[str]



    

   




    



