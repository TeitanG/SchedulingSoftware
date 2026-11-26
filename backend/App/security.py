import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from App.config import get_settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password, password_hash)
    except UnknownHashError:
        return False


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expiration = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    content = {"sub": str(user_id), "exp": expiration}
    encode = jwt.encode(content, settings.secret_key, algorithm=settings.algorithm)

    return encode


def decode_access_token(token: str) -> uuid.UUID | None:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
        return uuid.UUID(str(payload["sub"]))

    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
