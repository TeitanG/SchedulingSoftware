from datetime import UTC, datetime
from enum import Enum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import phonenumbers

NAME_MAX = 120
ADDRESS_MAX = 255
EMAIL_MAX = 255
PHONE_MAX = 20
TIMEZONE_MAX = 64
DESCRIPTION_MAX = 255
NOTES_MAX = 255
BOOKING_CODE_MAX = 20
CONSENT_VERSION_MAX = 20
PASSWORD_HASH_MAX = 255
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


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


class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    canceled = "canceled"


class DaysOfTheWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


WEEKDAYS = (
    DaysOfTheWeek.monday,
    DaysOfTheWeek.tuesday,
    DaysOfTheWeek.wednesday,
    DaysOfTheWeek.thursday,
    DaysOfTheWeek.friday,
    DaysOfTheWeek.saturday,
    DaysOfTheWeek.sunday,
)
