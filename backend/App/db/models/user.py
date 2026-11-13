import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, text
from sqlmodel import Field, SQLModel

from .common import utc_now


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    __table_args__ = (
        Index("users_email_unique", text("lower(email)"), unique=True),
        CheckConstraint("length(trim(name)) >0", name="users_name_not_blank"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=120)
    email: str = Field(max_length=255)
    active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )
