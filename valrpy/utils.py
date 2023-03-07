import time
import hashlib
import hmac


def sign_request(api_key_secret: str, verb: str, path: str, body: str = "") -> str:
    payload = f"{round(1e3 * time.time())}{verb}{path}{body}"
    signature = hmac.new(
        key=api_key_secret.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha512,
    ).hexdigest()
    return signature
