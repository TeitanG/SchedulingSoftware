import uuid
from datetime import datetime, time
from enum import Enum

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


class Avaibility(SQLModel, table=True):
    __tablename__ = "availabilities"  # type: ignore
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="start_time_before_end_time"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    member_id: uuid.UUID = Field(foreign_key="business_members.id", ondelete="RESTRICT")
    day: DaysOfTheWeek
    start_time: time
    end_time: time
    active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"onupdate": utc_now},
    )
