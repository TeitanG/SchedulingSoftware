import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from .common import utc_now


class ProviderService(SQLModel, table=True):
    __tablename__ = "provider_services"  # type: ignore

    member_id: uuid.UUID = Field(
        foreign_key="business_members.id", primary_key=True, ondelete="RESTRICT"
    )
    service_id: uuid.UUID = Field(
        foreign_key="services.id", primary_key=True, ondelete="RESTRICT"
    )
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime(timezone=True)
    )


class ProviderServicePublic(SQLModel):
    member_id: uuid.UUID
    service_id: uuid.UUID
    created_at: datetime


class ProviderServiceCreate(SQLModel):
    member_id: uuid.UUID
