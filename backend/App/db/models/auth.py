from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from App.db.models.common import PASSWORD_MAX_LENGTH


class LoginRequest(SQLModel):
    email: EmailStr
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
