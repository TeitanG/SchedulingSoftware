import psycopg
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def conflict_message(error: IntegrityError, UNIQUE_MESSAGES: dict) -> str | None:
    original = error.orig
    if not isinstance(original, psycopg.Error):
        return None
    constraint = original.diag.constraint_name
    if constraint is None:
        return None
    return UNIQUE_MESSAGES.get(constraint)


def response_404(type_of_missing: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"Error": f"{type_of_missing} not found"},
    )


def response_409(type_of_missing: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"Error": f"{type_of_missing} not active"},
    )


def response_401_login():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"Error": "Incorrect email or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def response_403():
    return HTTPException(
        status_code=status.HTTP_403_UNAUTHORIZED,
        detail={"Error": "Account is inactive"},
    )


def response_401_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"Error": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
