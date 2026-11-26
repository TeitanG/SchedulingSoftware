from App.db.models.user import User
from App.repositories.user import UserRepository
from App.security import create_access_token, decode_access_token, verify_password
from App.service.errors import (
    response_401_login,
    response_401_token,
    response_403,
)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, email: str, password: str) -> str:

        user = self.user_repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise response_401_login()

        if not user.active:
            raise response_403()
        return create_access_token(user.id)

    def get_current_user(self, token: str) -> User:
        access = decode_access_token(token)
        if access is None:
            raise response_401_token()

        user = self.user_repo.get(access)

        if user is None:
            raise response_401_token()

        if not user.active:
            raise response_401_token()

        return user
