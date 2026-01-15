from fastapi import APIRouter, Depends
from App.db.schemas import BusinessCreate, business_to_dict, BusinessPatch, BussinessPut
from App.db.client import db_client
from App.service import (create_business, search_business_by_id, 
                         delete_businesses, patch_business,
                         put_bussiness, search_all_businesses)
from App.dependencies import get_business_repository 
from App.repositories import BusinessRepository

router = APIRouter(
    prefix= "/businesses",
    tags=["businesses"]
)

@router.get("/")
async def get_businesses(business_repo: BusinessRepository = Depends(get_business_repository)):
    businesses = search_all_businesses(business_repo)
    return businesses

@router.get("/{id}")
async def get_one_business(id: str,
                           business_repo: BusinessRepository = Depends(get_business_repository)):
    return search_business_by_id(id, business_repo)

@router.post("/")
async def create_businesses(business : BusinessCreate,
                            business_repo : BusinessRepository =Depends(get_business_repository)):
    new_business = create_business(**business.model_dump(),
                                   business_repo=business_repo)
    return new_business
    

@router.put("/{id}")
async def update_entire_business(id:str, data:BussinessPut,
                                 business_repo : BusinessRepository =Depends(get_business_repository)):
    updated_business = put_bussiness(id, data, business_repo)
    return updated_business

@router.patch("/{id}")
async def update_business(id : str, data: BusinessPatch,
                          business_repo : BusinessRepository =Depends(get_business_repository)):
    update_patch_business = patch_business(id, data, business_repo)
    return update_patch_business

@router.delete("/{id}")
async def deleted_business(id : str,
                           business_repo : BusinessRepository =Depends(get_business_repository)):
    return delete_businesses(id, business_repo)


