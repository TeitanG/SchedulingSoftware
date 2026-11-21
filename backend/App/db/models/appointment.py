import uuid
from datetime import datetime

from pydantic import AwareDatetime, field_validator
from sqlalchemy import CheckConstraint, DateTime, Index
from sqlmodel import Field, SQLModel

from .common import (
    BOOKING_CODE_MAX,
    NOTES_MAX,
    AppointmentStatus,
    empty_to_none,
    utc_now,
)


class AppointmentBase(SQLModel):
    starts_at: datetime = Field(sa_type=DateTime(timezone=True))
    notes: str | None = Field(max_length=NOTES_MAX)


class Appointment(AppointmentBase, table=True):
    __tablename__ = "appointments"  # type: ignore
    __table_args__ = (
        CheckConstraint("starts_at < ends_at", name="appointments_starts_before_ends"),
        Index("appointments_booking_code_unique", "booking_code", unique=True),
        Index("appointments_provider_starts", "provider_id", "starts_at"),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    booking_code: str = Field(max_length=BOOKING_CODE_MAX)
    provider_id: uuid.UUID = Field(
        foreign_key="business_members.id", ondelete="RESTRICT"
    )
    client_id: uuid.UUID = Field(foreign_key="customers.id", ondelete="RESTRICT")
    service_id: uuid.UUID = Field(foreign_key="services.id", ondelete="RESTRICT")
    ends_at: datetime = Field(sa_type=DateTime(timezone=True))
    status: AppointmentStatus = Field(default=AppointmentStatus.pending)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
    )


class AppointmentCreate(AppointmentBase):
    client_id: uuid.UUID
    provider_id: uuid.UUID
    # TODO Login
    service_id: uuid.UUID
    starts_at: AwareDatetime

    @field_validator("notes")
    @classmethod
    def check_note(cls, value: str | None) -> str | None:
        return empty_to_none(value)


class AppointmentPublic(AppointmentBase):
    id: uuid.UUID
    booking_code: str
    client_id: uuid.UUID
    provider_id: uuid.UUID
    service_id: uuid.UUID
    ends_at: datetime
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime


class AppointmentStatusUpdate(SQLModel):
    status: AppointmentStatus


class AppointmentNotesUpdate(SQLModel):
    notes: str | None = Field(max_length=NOTES_MAX)

    @field_validator("notes")
    @classmethod
    def check_notes(cls, value: str | None) -> str | None:
        return empty_to_none(value)
