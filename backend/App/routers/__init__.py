from fastapi import APIRouter

from . import (
    # appointment,
    # availability_routers,
    business,
    docs_router,
    # service_routers,
    user,
)

router = APIRouter()

# router.include_router(appointment.router)
router.include_router(user.router)
# router.include_router(service_routers.router)
router.include_router(business.router)
# router.include_router(availability_routers.router)
router.include_router(docs_router.router)
