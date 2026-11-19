import uuid
from datetime import datetime, time
from enum import Enum

from pydantic import field_validator, model_validator
from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, SQLModel

from .common import utc_now


class DaysOfTheWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class AvailabilityBase(SQLModel):
    day: DaysOfTheWeek
    start_time: time
    end_time: time
    active: bool = Field(default=True)


class Availability(AvailabilityBase, table=True):
    __tablename__ = "availabilities"  # type: ignore
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="start_time_before_end_time"),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    member_id: uuid.UUID = Field(foreign_key="business_members.id", ondelete="RESTRICT")
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
    )


class AvailabilityCreate(AvailabilityBase):
    @model_validator(mode="after")
    def check_times(self):
        if not (self.start_time < self.end_time):
            raise ValueError("Start time cannot be after end_time")
        return self


class AvailabilityPublic(AvailabilityBase):
    id: uuid.UUID
    member_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class AvailabilityUpdate(SQLModel):
    day: DaysOfTheWeek | None = Field(default=None)
    start_time: time | None = Field(default=None)
    end_time: time | None = Field(default=None)
    active: bool | None = Field(default=None)

    @field_validator("day", "start_time", "end_time", "active")
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

