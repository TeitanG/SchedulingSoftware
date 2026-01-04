from App.db.models import daysOfTheWeek
from pydantic import BaseModel
from datetime import datetime


class AvailableBase(BaseModel):
    provider_id : str
    business_id : str
    day : daysOfTheWeek
    start_time : datetime
    end_time : datetime
    active : bool



def availability_to_dict(availability):
    return{
        "id": str(availability["_id"]),
        "provider_id" : str(availability["provider_id"]),
        "business_id" : str(availability["business_id"]),
        "day": availability["day"].value if hasattr(availability["day"],"value") else availability["day"],
        "start_time" : availability["start_time"],
        "end_time" : availability["end_time"],
        "active" : availability["active"],
    }


class AvailabilityPatch(BaseModel):
    provider_id : str | None = None
    business_id : str | None = None
    day : daysOfTheWeek | None = None
    start_time : datetime | None = None
    end_time : datetime | None = None
    active : bool | None = None


class AvailabilityCreate(AvailableBase):
    pass

class PutAvailability(AvailableBase):
    pass

