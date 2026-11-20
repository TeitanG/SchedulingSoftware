import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from App.db.models.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: uuid.UUID) -> Customer:
        pass

    @abstractmethod
    def add(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    def update(self, customer: Customer, changed: dict) -> Customer:
        pass

    @abstractmethod
    def list_by_business(
        self, business_id: uuid.UUID, *, active: bool, limit: int, offset: int
    ) -> list[Customer]:
        pass


class SQLCustomerRepository(CustomerRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, customer_id: uuid.UUID) -> Customer | None:
        return self.session.get(Customer, customer_id)
