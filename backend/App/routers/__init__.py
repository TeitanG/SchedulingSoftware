from fastapi import APIRouter

from . import (
    appointment_routers,
    availability_routers,
    business_routers,
    docs_router,
    service_routers,
    user_routers,
)

router = APIRouter()

router.include_router(appointment_routers.router)
router.include_router(user_routers.router)
router.include_router(service_routers.router)
router.include_router(business_routers.router)
router.include_router(availability_routers.router)
router.include_router(docs_router.router)
