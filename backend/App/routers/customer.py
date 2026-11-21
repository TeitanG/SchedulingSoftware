import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from App.db.models.customer import (
    Customer,
    CustomerCreate,
    CustomerPublic,
    CustomerUpdate,
)
from App.dependencies.dependencies import CustomerServiceDep

router = APIRouter(prefix="/business/{business_id}/customer", tags=["customer"])


@router.post("/", response_model=CustomerPublic, status_code=status.HTTP_201_CREATED)
def create_customer(
    service: CustomerServiceDep, business_id: uuid.UUID, data: CustomerCreate
) -> Customer:
    return service.create(business_id, data)


@router.get("/{customer_id}", response_model=CustomerPublic)
def get_customer(
    service: CustomerServiceDep, customer_id: uuid.UUID, business_id: uuid.UUID
) -> Customer:
    return service.get(business_id=business_id, customer_id=customer_id)


@router.get("/", response_model=list[CustomerPublic])
def list_customers(
    service: CustomerServiceDep,
    business_id: uuid.UUID,
    active: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Customer]:
    return service.list_by_business(
        business_id, active=active, limit=limit, offset=offset
    )


@router.patch("/{customer_id}", response_model=CustomerPublic)
def update_customer(
    service: CustomerServiceDep,
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    data: CustomerUpdate,
) -> Customer:
    return service.update(business_id=business_id, customer_id=customer_id, data=data)
