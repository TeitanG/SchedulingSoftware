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
