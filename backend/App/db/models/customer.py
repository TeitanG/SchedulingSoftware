import uuid
from datetime import datetime
from typing import Self

from pydantic import EmailStr, field_validator, model_validator
from sqlalchemy import CheckConstraint, DateTime, Index, func, text
from sqlmodel import Field, SQLModel

from App.db.models.common import (
    CONSENT_VERSION_MAX,
    EMAIL_MAX,
    NAME_MAX,
    PHONE_MAX,
    clean_name,
    normalize_phone,
    utc_now,
)


class CustomerBase(SQLModel):
    name: str = Field(max_length=NAME_MAX)
    email: str | None = Field(default=None, max_length=EMAIL_MAX)
    phone_number: str | None = Field(default=None, max_length=PHONE_MAX)


class Customer(CustomerBase, table=True):
    __tablename__ = "customers"  # type: ignore
    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR phone_number IS NOT NULL",
            name="customers_email_or_phone_number",
        ),
        Index(
            "customers_business_email_unique",
            "business_id",
            func.lower(text("email")),
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
        ),
        Index(
            "customers_business_phone_unique",
            "business_id",
            "phone_number",
            unique=True,
            postgresql_where=text("phone_number IS NOT NULL"),
        ),
        Index(
            "customers_business_user_unique",
            "business_id",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="businesses.id", ondelete="RESTRICT")
    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="users.id", ondelete="RESTRICT"
    )
    email_verified_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
    phone_verified_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )
    consent_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    consent_version: str = Field(max_length=CONSENT_VERSION_MAX)
    active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
    )


class CustomerCreate(CustomerBase):
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX)
    consent: bool

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        return clean_name(value)

    @field_validator("email")
    @classmethod
    def lower_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.lower()

    @field_validator("phone_number")
    @classmethod
    def check_phone_number(cls, value: str) -> str | None:
        if value is None:
            return None
        return normalize_phone(value)

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("You must accept the personal data policy")
        return value

    @model_validator(mode="after")
    def require_contact(self) -> Self:
        if self.email is None and self.phone_number is None:
            raise ValueError("Provide at least an email or a phone")
        return self


class CustomerPublic(CustomerBase):
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: uuid.UUID | None
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    consent_at: datetime
    consent_version: str
    active: bool
    created_at: datetime
    updated_at: datetime


class CustomerUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=NAME_MAX)
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX)
    phone_number: str | None = Field(default=None, max_length=PHONE_MAX)
    active: bool | None = Field(default=None)

    @field_validator("name", "active")
    @classmethod
    def reject_null(cls, value: str | bool | None) -> str | bool | None:
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        return clean_name(value)

    @field_validator("email")
    @classmethod
    def lower_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.lower()

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_phone(value)
