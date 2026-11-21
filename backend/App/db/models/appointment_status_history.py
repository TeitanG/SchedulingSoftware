import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index
from sqlmodel import Field, SQLModel

from .common import AppointmentStatus, utc_now


class AppointmentStatusHistory(SQLModel, table=True):
    __tablename__ = "appointments_status_history"  # type: ignore
    __table_args__ = (
        Index(
            "appointments_status_history_appointment_changed",
            "appointment_id",
            "changed_at",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    appointment_id: uuid.UUID = Field(
        foreign_key="appointments.id", ondelete="RESTRICT"
    )
    old_status: AppointmentStatus | None = Field(default=None)
    new_status: AppointmentStatus
    changed_by: uuid.UUID | None = Field(
        default=None, foreign_key="users.id", ondelete="RESTRICT"
    )
    changed_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
    )


class AppointmentStatusHistoryPublic(SQLModel):
    id: uuid.UUID
    appointment_id: uuid.UUID
    old_status: AppointmentStatus | None
    new_status: AppointmentStatus
    changed_at: datetime
    changed_by: uuid.UUID | None = Field(default=None)
