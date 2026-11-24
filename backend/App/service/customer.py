import uuid
from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from App.db.models.customer import Customer, CustomerCreate, CustomerUpdate
from App.repositories.business import BusinessRepository
from App.repositories.customer import CustomerRepository
from App.service.errors import conflict_message, response_404, response_409

UNIQUE_MESSAGES = {
    "customers_business_email_unique": "A customer with that email already exists in this business",
    "customers_business_phone_unique": "A customer with that phone number already exists in this business",
    "customers_business_user_unique": "This user is already a customer of this business",
}

CONSENT_VERSION = "2026-11-19"


class CustomerService:
    def __init__(self, repo: CustomerRepository, business_repo: BusinessRepository):
        self.repo = repo
        self.business_repo = business_repo

    def _raise_if_conflict(self, error: IntegrityError) -> NoReturn:
        message = conflict_message(error, UNIQUE_MESSAGES)
        if message is None:
            raise error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"Error": message}
        )

    def get(self, business_id: uuid.UUID, customer_id: uuid.UUID) -> Customer:
        customer = self.repo.get(customer_id)

        if customer is None or customer.business_id != business_id:
            raise response_404("Customer")

        return customer

    def create(
        self,
        business_id: uuid.UUID,
        data: CustomerCreate,
    ) -> Customer:
        business = self.business_repo.get(business_id)

        if not business:
            raise response_404("Business")

        if not business.active:
            raise response_409("Business")

        customer = Customer(
            **data.model_dump(exclude={"consent"}),
            business_id=business_id,
            consent_version=CONSENT_VERSION,
        )

        try:
            return self.repo.add(customer)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def update(
        self, business_id: uuid.UUID, customer_id: uuid.UUID, data: CustomerUpdate
    ) -> Customer:

        customer = self.get(business_id=business_id, customer_id=customer_id)

        changes = data.model_dump(exclude_unset=True)

        email = changes.get("email", customer.email)
        phone = changes.get("phone_number", customer.phone_number)

        if email is None and phone is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"Error": "Customer must have an email or a phone number"},
            )

        try:
            return self.repo.update(customer, changes)
        except IntegrityError as error:
            self._raise_if_conflict(error)

    def list_by_business(
        self,
        business_id: uuid.UUID,
        *,
        active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Customer]:
        business = self.business_repo.get(business_id)

        if business is None:
            raise response_404("Business")

        if not business.active:
            raise response_409("Business")

        return self.repo.list_by_business(
            business_id, active=active, limit=limit, offset=offset
        )
