from fastapi import APIRouter

from App.db.models.auth import LoginRequest, TokenResponse
from App.dependencies.dependencies import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def post_auth(service: AuthServiceDep, data: LoginRequest) -> TokenResponse:
    token = service.login(data.email, data.password)
    return TokenResponse(access_token=token)
