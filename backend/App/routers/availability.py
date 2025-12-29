from fastapi import APIRouter


router = APIRouter(
    prefix= "/availabilities",
    tags=["availabilities"]
)

@router.get("/")
async def get_availabilities():
    pass


@router.get("/{id}")
async def get_one_availability(id: str):
    pass

@router.post("/")
async def create_availability():
    pass

@router.put("/{id}")
async def update_entire_availability():
    pass

@router.patch("/{id}")
async def update_availability():
    pass

@router.delete("/{id}")
async def delete_availability():
    pass
