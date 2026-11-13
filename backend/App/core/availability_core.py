from datetime import time

TIME_FORMAT = "%H:%M"


def time_to_db(value: time) -> str:
    return value.strftime(TIME_FORMAT)


def time_from_db(value: str) -> time:
    return time.fromisoformat(value)
