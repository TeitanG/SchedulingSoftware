import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Index
from sqlmodel import Field, SQLModel

from .common import utc_now


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "canceled"


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"  # type: ignore
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="appointments_starts_before_ends"),
        Index("appointments_booking_code_unique", "booking_code", unique=True),
        Index("appointments_provider_starts", "provider_id", "starts_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_code: str = Field(max_length=20)
    client_id: uuid.UUID = Field(foreign_key="users.id", ondelete="RESTRICT")
    provider_id: uuid.UUID = Field(
        foreign_key="business_members.id", ondelete="RESTRICT"
    )
    service_id: uuid.UUID = Field(foreign_key="services.id", ondelete="RESTRICT")
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    status: AppointmentStatus = Field(default=AppointmentStatus.pending)
    notes: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
    )
