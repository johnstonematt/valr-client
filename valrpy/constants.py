from datetime import timezone
from decimal import Decimal
from typing import TypeAlias


__all__ = [
    "Number",
    "DATETIME_FORMAT",
    "TIMEZONE",
]


Number: TypeAlias = int | float | Decimal

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

TIMEZONE = timezone.utc
