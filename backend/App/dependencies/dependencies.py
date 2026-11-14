from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from App.db.engine import get_session
from App.repositories.sql_repositories import SQLBusinessRepository, SQLUserRepository
from App.service.business import BusinessService
from App.service.user import UserService

SessionDep = Annotated[Session, Depends(get_session)]


def get_business_service(session: SessionDep) -> BusinessService:
    return BusinessService(SQLBusinessRepository(session))


def get_user_service(session: SessionDep) -> UserService:
    return UserService(SQLUserRepository(session))


BusinessServiceDep = Annotated[BusinessService, Depends(get_business_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
