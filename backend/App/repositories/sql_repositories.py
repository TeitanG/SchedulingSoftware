import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from App.db.models import Business

from .repositories import BusinessRepository


class SQLBusinessRepository(BusinessRepository):
    def __init__(self, session: Session):
        self.session = session
   

    def get(self, business_id: uuid.UUID) -> Business | None:
        return self.session.get(Business, business_id)

    def list_all(
        self, *, active: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Business]:
        statement = select(Business).order_by(Business.name).offset(offset).limit(limit)
        if active is not None:
            statement = statement.where(Business.active == active)
        return list(self.session.exec(statement).all())

    def add(self, business: Business) -> Business:
        self.session.add(business)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(business)
        return business

    def update(self, business: Business, changes: dict) -> Business:
        # for field, value in changes.items():
        #     setattr(business, field, value)
        business.sqlmodel_update(changes)
        self.session.add(business)
        self.session.commit()
        self.session.refresh(business)
        return business
