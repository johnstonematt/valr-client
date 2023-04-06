from datetime import timezone


__all__ = [
    "DATETIME_FORMAT",
    "TIMEZONE",
]


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

TIMEZONE = timezone.utc
