from fastapi import APIRouter, Depends
from bson import ObjectId
from App.service import (create_availability, search_availability,
                          delete_availability, patch_availability,
                          put_availability, search_availabilities)
from App.db.schemas import (AvailabilityCreate,
                             AvailabilityPatch, PutAvailability)
from App.dependencies import (get_availability_repository,
                              get_business_repository, 
                              get_user_repository)
from App.repositories import (AvailabilityRepository,
                              UserRepository, BusinessRepository,
                              )



router = APIRouter(
    prefix= "/availabilities",
    tags=["availabilities"]
)

@router.get("/")
async def get_availabilities(Availability_repo : AvailabilityRepository = Depends(get_availability_repository)):
    return search_availabilities(Availability_repo)




@router.get("/{id}")
async def get_one_availability(id: str,
                               availability_repo :AvailabilityRepository = Depends(get_availability_repository) ):
    return search_availability(id, availability_repo)

@router.post("/")
async def create_availabilities(availability : AvailabilityCreate,
                                availability_repo : AvailabilityRepository = Depends(get_availability_repository)):
    new_availability = create_availability(**availability.model_dump(),
                                           availability_repo = availability_repo)
    return new_availability
    

@router.put("/{id}")
async def update_entire_availability(id: str, PutAvailability: PutAvailability,
                                     availability_repo : AvailabilityRepository = Depends(get_availability_repository)):
    updated_availability = put_availability(id, PutAvailability, availability_repo)
    return updated_availability
    

@router.patch("/{id}")
async def update_availability(id: str, availability :AvailabilityPatch,
                              availability_repo : AvailabilityRepository = Depends(get_availability_repository),
                              user_repo: UserRepository = Depends(get_user_repository),
                              business_repo: BusinessRepository = Depends(get_business_repository)):
    updated_availability = patch_availability(id, availability, availability_repo, user_repo, business_repo)
    return updated_availability

@router.delete("/{id}")
async def deleted_availability(id : str, availability_repo : AvailabilityRepository = Depends(get_availability_repository)):
    return delete_availability(id, availability_repo)
