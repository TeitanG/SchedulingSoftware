from fastapi import APIRouter


router = APIRouter(
    prefix= "/businesses",
    tags=["businesses"]
)

@router.get("/")
async def get_businesses():
    pass


@router.get("/{id}")
async def get_one_business(id: str):
    pass

@router.post("/")
async def create_business():
    pass

@router.put("/{id}")
async def update_entire_business():
    pass

@router.patch("/{id}")
async def update_business():
    pass

@router.delete("/{id}")
async def delete_business():
    pass


