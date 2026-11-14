from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from App.db.engine import get_session
from App.repositories.sql_repositories import SQLBusinessRepository
from App.service import BusinessService

SessionDep = Annotated[Session, Depends(get_session)]


def get_business_service(session: SessionDep) -> BusinessService:
    return BusinessService(SQLBusinessRepository(session))


BusinessServiceDep = Annotated[BusinessService, Depends(get_business_service)]
