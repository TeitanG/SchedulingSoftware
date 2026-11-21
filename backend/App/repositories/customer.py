import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: uuid.UUID) -> Customer | None:
        pass

    @abstractmethod
    def add(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    def update(self, customer: Customer, changes: dict) -> Customer:
        pass

    @abstractmethod
    def list_by_business(
        self, business_id: uuid.UUID, *, active: bool | None, limit: int, offset: int
    ) -> list[Customer]:
        pass


class SQLCustomerRepository(CustomerRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, customer_id: uuid.UUID) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def add(self, customer: Customer) -> Customer:
        self.session.add(customer)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(customer)
        return customer

    def update(self, customer: Customer, changes: dict) -> Customer:
        customer.sqlmodel_update(changes)
        self.session.add(customer)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        self.session.refresh(customer)
        return customer

    def list_by_business(
        self, business_id: uuid.UUID, *, active: bool | None, limit: int, offset: int
    ) -> list[Customer]:
        statement = (
            select(Customer)
            .where(Customer.business_id == business_id)
            .order_by(col(Customer.name), col(Customer.id))
            .offset(offset)
            .limit(limit)
        )
        if active is not None:
            statement = statement.where(Customer.active == active)

        return list(self.session.exec(statement).all())
