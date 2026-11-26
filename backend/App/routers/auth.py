from fastapi import APIRouter

from App.db.models.auth import LoginRequest, TokenResponse
from App.db.models.user import User, UserPublic
from App.dependencies.dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def post_auth(service: AuthServiceDep, data: LoginRequest) -> TokenResponse:
    token = service.login(data.email, data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: CurrentUserDep) -> User:
    return current_user
