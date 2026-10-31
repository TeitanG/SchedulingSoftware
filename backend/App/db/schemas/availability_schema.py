from datetime import time

from pydantic import BaseModel

from App.db.models import daysOfTheWeek


class AvailableBase(BaseModel):
    provider_id: str
    business_id: str
    day: daysOfTheWeek
    start_time: time
    end_time: time
    active: bool


def availability_to_dict(availability):
    return {
        "id": str(availability["_id"]),
        "provider_id": str(availability["provider_id"]),
        "business_id": str(availability["business_id"]),
        "day": availability["day"].value
        if hasattr(availability["day"], "value")
        else availability["day"],
        "start_time": availability["start_time"],
        "end_time": availability["end_time"],
        "active": availability["active"],
    }


def availabilities_to_dict(availabilities) -> list:
    result = []

    for availability in availabilities:
        result.append(availability_to_dict(availability))
    return result


class AvailabilityPatch(BaseModel):
    provider_id: str | None = None
    business_id: str | None = None
    day: daysOfTheWeek | None = None
    start_time: time | None = None
    end_time: time | None = None
    active: bool | None = None


class AvailabilityCreate(AvailableBase):
    pass


class PutAvailability(AvailableBase):
    pass
