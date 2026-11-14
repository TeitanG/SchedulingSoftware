import psycopg
from sqlalchemy.exc import IntegrityError


def conflict_message(error: IntegrityError, UNIQUE_MESSAGES: dict) -> str | None:
    original = error.orig
    if not isinstance(original, psycopg.Error):
        return None
    constraint = original.diag.constraint_name
    if constraint is None:
        return None
    return UNIQUE_MESSAGES.get(constraint)
