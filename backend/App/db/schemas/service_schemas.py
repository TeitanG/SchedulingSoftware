from pydantic import BaseModel


class ServiceBase(BaseModel):
    name : str
    description : str | None = None
    price : int | None = None
    provider_id : str
    business_id : str 
    duration : int
    capacity : int



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
        "capacity": service["capacity"]
    }

class ServicePatch(BaseModel):
    name : str | None = None
    description : str | None = None
    price : int | None = None
    provider_id : str | None = None
    business_id : str | None = None
    duration : int | None = None
    capacity : int | None = None


class ServiceCreate(ServiceBase):
    pass

class ServicePut(ServiceBase):
    pass


