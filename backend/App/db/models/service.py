import uuid
from datetime import datetime

from pydantic import field_validator
from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import DESCRIPTION_MAX, NAME_MAX, clean_name, empty_to_none, utc_now


class ServiceBase(SQLModel):
    name: str = Field(max_length=NAME_MAX)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX)
    price_amount: int = Field(gt=0)
    duration: int = Field(gt=0)
    capacity: int = Field(default=1, ge=1)
    active: bool = Field(default=True)


class Service(ServiceBase, table=True):
    __tablename__ = "services"  # type: ignore
    __table_args__ = (
        Index(
            "services_business_name_unique",
            "business_id",
            text("lower(name)"),
            unique=True,
        ),
        CheckConstraint("length(trim(name)) > 0", name="services_name_not_blank"),
        CheckConstraint("price_amount >= 0", name="services_price_non_negative"),
        CheckConstraint("duration > 0", name="services_duration_positive"),
        CheckConstraint("capacity>= 1", name="services_capacity_min_one"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(foreign_key="businesses.id", ondelete="RESTRICT")

    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(
            timezone=True,
        ),
        sa_column_kwargs={"onupdate": utc_now},
    )


class ServicePublic(ServiceBase):
    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ServiceCreate(ServiceBase):
    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        return clean_name(value)

    @field_validator("description")
    @classmethod
    def check_description(cls, value: str | None) -> str | None:
        return empty_to_none(value)


class ServiceUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=NAME_MAX)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX)
    price_amount: int | None = Field(default=None, gt=0)
    duration: int | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, ge=1)
    active: bool | None = Field(default=None)

    @field_validator("name", "price_amount", "duration", "capacity", "active")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("name")
    @classmethod
    def check_name(cls, value) -> str | None:
        if value is None:
            return None
        return clean_name(value)

    @field_validator("description")
    @classmethod
    def check_description(cls, value: str | None) -> str | None:
        return empty_to_none(value)
