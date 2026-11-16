import uuid
from datetime import datetime

from pydantic import field_validator, model_validator
from sqlalchemy import CheckConstraint, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

from .common import utc_now


class BusinessMembersBase(SQLModel):
    is_admin: bool
    is_provider: bool
    active: bool = Field(default=True)


class BusinessMembers(BusinessMembersBase, table=True):
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

    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )


class BusinessMembersPublic(BusinessMembersBase):
    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime


class BusinessMembersCreate(BusinessMembersBase):
    user_id: uuid.UUID

    @model_validator(mode="after")
    def check_has_role(self):
        if not (self.is_admin or self.is_provider):
            raise ValueError("A member must be an admin, provider or both")
        return self


class BusinessMembersUpdate(SQLModel):
    is_admin: bool | None = Field(default=None)
    is_provider: bool | None = Field(default=None)
    active: bool | None = Field(default=None)

    @field_validator("is_admin", "is_provider", "active")
    def reject_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value
