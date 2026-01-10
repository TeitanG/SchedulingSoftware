from typing import Optional
from pydantic import BaseModel
from datetime import time, datetime
from enum import Enum

class daysOfTheWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class availability(BaseModel):
    id : Optional[str] = None
    provider_id : str
    business_id : str
    day : daysOfTheWeek
    start_time : time
    end_time : time
    duration : int
    active: bool
    capacity : int





