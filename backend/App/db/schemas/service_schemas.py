from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name : str
    description : str | None = None
    price : int | None = None
    provider_id : str
    business_id : str 
    duration : int
    capacidad : int



def service_to_dict(service)-> dict:
    return{
        "id" : str(service["_id"]),
        "name" : service["name"],
        "description" :(
             service["description"]
             if service.get("description") is not None
             else None),
        "price" : (
            service["price"]
            if service.get("price") is not None
            else None),
        "provider_id" : service["provider_id"],
        "business_id": (
            str(service["business_id"])
            if service.get("business_id") is not None
            else None),  
        "duration": service["duration"],
        "capacidad": service["capacidad"]
    }

class PatchUpdateService(BaseModel):
    name : str | None = None
    description : str | None = None
    price : int | None = None
    provider_id : str | None = None
    business_id : str | None = None
    duration : int | None = None
    capacidad : int | None = None


