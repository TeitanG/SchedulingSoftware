import uuid
from datetime import datetime

from pydantic import EmailStr, field_validator
from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import (
    EMAIL_MAX,
    NAME_MAX,
    PASSWORD_HASH_MAX,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    clean_name,
    utc_now,
)


class UserBase(SQLModel):
    name: str = Field(max_length=NAME_MAX)
    email: str = Field(max_length=EMAIL_MAX)
    active: bool = Field(default=True)


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    __table_args__ = (
        Index("users_email_unique", text("lower(email)"), unique=True),
        CheckConstraint("length(trim(name)) >0", name="users_name_not_blank"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    password_hash: str = Field(max_length=PASSWORD_HASH_MAX)


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )

    @field_validator("name")
    @classmethod
    def check_name(cls, value) -> str:
        return clean_name(value)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=NAME_MAX)
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX)
    active: bool | None = Field(default=None)

    @field_validator("name", "email", "active")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("name")
    @classmethod
    def check_name(cls, value):
        return clean_name(value)
