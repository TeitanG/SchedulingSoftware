import uuid
from datetime import datetime
from enum import Enum

from pydantic import EmailStr, field_validator
from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import (
    ADDRESS_MAX,
    EMAIL_MAX,
    NAME_MAX,
    PHONE_MAX,
    TIMEZONE_MAX,
    clean_name,
    empty_to_none,
    normalize_phone,
    utc_now,
    validate_timezone,
)


class BusinessType(str, Enum):
    medical = "medical"
    beauty = "beauty"
    logistics = "logistics"
    custom = "custom"


class Currency(str, Enum):
    COP = "COP"
    USD = "USD"


class BusinessBase(SQLModel):
    name: str = Field(max_length=NAME_MAX)
    business_type: BusinessType
    address: str | None = Field(default=None, max_length=ADDRESS_MAX)
    email: str = Field(max_length=EMAIL_MAX)
    phone_number: str = Field(max_length=PHONE_MAX)
    timezone: str = Field(default="America/Bogota", max_length=TIMEZONE_MAX)
    currency: Currency = Field(default=Currency.COP)
    active: bool = Field(default=True)


class Business(BusinessBase, table=True):
    __tablename__ = "businesses"  # type: ignore
    __table_args__ = (
        Index("businesses_name_unique", text("lower(name)"), unique=True),
        Index("businesses_email_unique", text("lower(email)"), unique=True),
        CheckConstraint("length(trim(name)) > 0", name="businesses_name_not_blank"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )


class BusinessCreate(BusinessBase):
    email: EmailStr

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str) -> str:
        return validate_timezone(value)

    @field_validator("phone_number")
    @classmethod
    def check_phone_number(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("address")
    @classmethod
    def check_address(cls, value: str | None = None) -> str | None:
        return empty_to_none(value)

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        return clean_name(value)


class BusinessPublic(BusinessBase):
    id: uuid.UUID
    created_at: datetime


class BusinessUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=NAME_MAX)
    business_type: BusinessType | None = Field(default=None)
    address: str | None = Field(default=None, max_length=ADDRESS_MAX)
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX)
    phone_number: str | None = Field(default=None, max_length=PHONE_MAX)
    timezone: str | None = Field(default=None, max_length=TIMEZONE_MAX)
    active: bool | None = Field(default=None)

    @field_validator("timezone")
    @classmethod
    def check_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_timezone(value)

    @field_validator(
        "name", "business_type", "email", "phone_number", "timezone", "active"
    )
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("phone_number")
    @classmethod
    def check_phone_number(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("address")
    @classmethod
    def check_address(cls, value: str | None = None) -> str | None:
        return empty_to_none(value)

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        return clean_name(value)
