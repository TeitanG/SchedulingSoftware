from fastapi import APIRouter

from App.routers import provider_service

from . import (
    # appointment,
    # availability_routers,
    business,
    business_member,
    docs_router,
    service,
    user,
)

router = APIRouter()

# router.include_router(appointment.router)
router.include_router(user.router)
router.include_router(service.router)
router.include_router(business.router)
# router.include_router(availability_routers.router)
router.include_router(docs_router.router)
router.include_router(business_member.router)
router.include_router(provider_service.router)
