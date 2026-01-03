from App.db.models.business import BusinessType
from pydantic import BaseModel, EmailStr


class BusinessCreate(BaseModel):
    name : str
    business_type : BusinessType
    address : str | None = None
    email : EmailStr
    phone_number : str
    active : bool



def business_to_dict(business) -> dict:
    return{
        "id" : str(business["_id"]),
        "name" : business["name"],
        "business_type":business["business_type"].value 
        if hasattr(business["business_type"], "value")
        else business["business_type"],
        "address" : (
            business["address"]
            if business.get("address") is not None
            else None),
        "email" : business["email"],
        "phone_number": business["phone_number"],
        "active" : bool(business["active"])
    }

class PatchUpdateBusiness(BaseModel):
    name : str| None = None
    business_type : BusinessType| None = None
    address : str | None = None
    email : EmailStr| None = None
    phone_number : str| None = None
    active : bool| None = None

