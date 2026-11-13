import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from .common import utc_now


class BusinessMembers(SQLModel, table=True):
    __tablename__ = "business_members"  # type: ignore
    __table_args__ = (
        UniqueConstraint(
            "user_id", "business_id", name="business_members_user_business_unique"
        ),
        CheckConstraint("is_admin OR is_provider", name="business_members_has_role"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="RESTRICT")
    business_id: uuid.UUID = Field(foreign_key="businesses.id", ondelete="RESTRICT")
    is_admin: bool
    is_provider: bool
    active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )




