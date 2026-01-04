from fastapi import APIRouter

from ..service import user_routers
from . import appointment_routers, service_routers, business_routers, availability_routers

router = APIRouter()

router.include_router(appointment_routers.router)
router.include_router(user_routers.router)
router.include_router(service_routers.router)
router.include_router(business_routers.router)
router.include_router(availability_routers.router)



