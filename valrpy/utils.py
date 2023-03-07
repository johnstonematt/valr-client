import hashlib
import hmac


def request_signature(
    api_key_secret: str, method: str, path: str, body: str, timestamp: int
) -> str:
    payload = f"{timestamp}{method}{path}{body}"
    signature = hmac.new(
        key=api_key_secret.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).hexdigest()
    return signature
