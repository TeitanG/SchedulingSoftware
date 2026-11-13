import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import utc_now


class BusinessType(str, Enum):
    medical = "medical"
    beauty = "beauty"
    logistics = "logistics"
    custom = "custom"


class Currency(str, Enum):
    COP = "COP"
    USD = "USD"
    
class Business(SQLModel, table=True):
    __tablename__ = "businesses"  # type: ignore
    __table_args__ = (
        Index("businesses_name_unique", text("lower(name)"), unique=True),
        Index("businesses_email_unique", text("lower(email)"), unique=True),
        CheckConstraint("length(trim(name)) > 0", name="businesses_name_not_blank"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=120)
    business_type : BusinessType
    address : str | None = Field(default=None, max_length=255)
    email: str = Field(max_length=255)
    phone_number : str =Field(max_length=255)
    timezone: str = Field(default="America/Bogota", max_length=64)
    currency : Currency = Field(default=Currency.COP)
    active : bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
