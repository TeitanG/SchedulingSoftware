from fastapi import APIRouter
from App.db.schemas import BusinessCreate, business_to_dict
from App.db.client import db_client
from App.service import create_business, search_business, delete_businesses
from bson import ObjectId
 




router = APIRouter(
    prefix= "/businesses",
    tags=["businesses"]
)

@router.get("/")
async def get_businesses():
    return[business_to_dict(business)for business in db_client.businesses.find()]

@router.get("/{id}")
async def get_one_business(id: str):
    return search_business("_id", id)

@router.post("/")
async def create_businesses(business : BusinessCreate ):
    new_business = create_business(**business.model_dump())
    return new_business
    

@router.put("/{id}")
async def update_entire_business():
    pass

@router.patch("/{id}")
async def update_business():
    pass

@router.delete("/{id}")
async def deleted_business(id : str):
    return delete_businesses("_id", id)


