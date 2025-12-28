from typing import Optional
from pydantic import BaseModel
from datetime import timedelta, time, datetime
from enum import Enum

class status_appointments(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "Cancecanceledlado"

class Appointment(BaseModel):
    id : Optional[str] = None
    client_id : str
    provider_id : str
    service_id : str
    business_id: str
    start_time : datetime
    end_time: Optional[datetime] = None
    duration : int
    status_ : status_appointments
    notes : Optional[str]


    def endTimeFun(self):
        self.end_time = self.start_time + timedelta(minutes=self.duration)


    



