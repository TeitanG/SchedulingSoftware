from App.db.models import daysOfTheWeek
from pydantic import BaseModel
from datetime import datetime


class CreateAvailability(BaseModel):
    provider_id : str
    business_id : str
    day : daysOfTheWeek
    start_time : datetime
    end_time : datetime
    duration : int
    active : bool
    capacity : int



def availability_to_dict(availability):
    return{
        "id": str(availability["_id"]),
        "provider_id" : str(availability["provider_id"]),
        "business_id" : str(availability["business_id"]),
        "day": availability["day"].value if hasattr(availability["day"],"value") else availability["day"],
        "start_time" : availability["start_time"],
        "end_time" : availability["end_time"],
        "duration" : availability["duration"],
        "active" : availability["active"],
        "capacity" : availability["capacity"]
    }
