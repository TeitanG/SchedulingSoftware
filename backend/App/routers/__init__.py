from fastapi import APIRouter
from . import appointment_routers, user_routers, service_routers

router = APIRouter()

router.include_router(appointment_routers.router)
router.include_router(user_routers.router)
router.include_router(service_routers.router)



