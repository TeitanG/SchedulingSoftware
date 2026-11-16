from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import phonenumbers

NAME_MAX = 120
ADDRESS_MAX = 255
EMAIL_MAX = 255
PHONE_MAX = 20
TIMEZONE_MAX = 64
DESCRIPTION_MAX = 255


def utc_now() -> datetime:
    return datetime.now(UTC)


def validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"Unkown timezone: {value}")
    return value


def normalize_phone(
    value: str,
):
    try:
        parsed = phonenumbers.parse(value, None)
    except phonenumbers.NumberParseException:
        raise ValueError("Use international format, example: +573001234567")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Phone number invalid")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def clean_name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Name cannot be empty")
    return value
