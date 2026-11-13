import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import utc_now


class Service(SQLModel, table=True):
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
    name: str = Field(max_length=120)
    description: str | None = Field(default=None, max_length=255)
    price_amount: int
    duration: int
    capacity: int = Field(default=1)
    active: bool = Field(default=True)
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
