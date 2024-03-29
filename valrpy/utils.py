import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any


__all__ = [
    "RestException",
    "enforce_type",
    "datetime_to_milliseconds",
    "request_signature",
    "generate_headers",
]


class RestException(Exception):
    """
    Raised when rest problems occur.
    """

    pass


def enforce_type(obj: Any, obj_type: type) -> None:
    if not isinstance(obj, obj_type):
        raise TypeError(
            f"Expected obj to be of type {obj_type.__name__} but instead received "
            f"{type(obj).__name__}: {obj}"
        )


def datetime_to_milliseconds(dt: Optional[datetime]) -> Optional[int]:
    if dt is not None:
        return int(1e3 * dt.timestamp())


def request_signature(
    api_secret: str,
    method: str,
    path: str,
    body: str | dict,
    timestamp: int,
    subaccount_id: Optional[str],
) -> str:
    if isinstance(body, dict):
        body = json.dumps(body)

    payload = f"{timestamp}{method.upper()}{path}{body}"
    if subaccount_id is not None:
        payload = f"{payload}{subaccount_id}"

    signature = hmac.new(
        key=api_secret.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).hexdigest()
    return signature


def generate_headers(
    api_key: str,
    api_secret: str,
    method: str,
    path: str,
    body: str | dict,
    subaccount_id: Optional[str] = None,
) -> Dict[str, str]:
    timestamp = int(1e3 * time.time())
    signature = request_signature(
        api_secret=api_secret,
        method=method,
        path=path,
        body=body,
        subaccount_id=subaccount_id,
        timestamp=timestamp,
    )
    headers = {
        "X-VALR-API-KEY": api_key,
        "X-VALR-SIGNATURE": signature,
        "X-VALR-TIMESTAMP": str(timestamp),
    }
    if subaccount_id is not None:
        headers["X-VALR-SUB-ACCOUNT-ID"] = subaccount_id

    return headers
