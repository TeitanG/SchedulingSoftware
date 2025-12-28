from pydantic import BaseModel


class serviceCreate(BaseModel):
    name : str
    description : str | None = None
    price : int | None = None
    provider_id : str
    business_id : str 



def serviceSchema(service)-> dict:
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
    }

