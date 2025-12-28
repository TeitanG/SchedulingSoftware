from typing import Optional
from pydantic import BaseModel
from datetime import time, datetime
from enum import Enum

class daysOfTheWeek(str, Enum):
    MONDAY = "Lunes"
    TUESDAY = "Martes"
    WEDNESDAY = "Miércoles"
    THURSDAY = "Jueves"
    FRIDAY = "Viernes"
    SATURDAY = "Sábado"
    SUNDAY = "Domingo"


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





