"""Request authentication for the orders API."""

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

SECRET = b"replace-me-in-config"
CLOCK_SKEW_SECONDS = 30


class AuthError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass
class Principal:
    user_id: str
    scopes: tuple


def _b64decode(value):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _signature_valid(payload, signature):
    expected = hmac.new(SECRET, payload, hashlib.sha256).digest()
    return hmac.compare_digest(expected, signature)


def authenticate(headers):
    """Turn an Authorization header into a Principal, or raise AuthError.

    Tokens look like ``<base64url(payload json)>.<base64url(hmac-sha256)>``.
    """
    header = headers.get("Authorization")
    if header is None:
        raise AuthError(401, "missing credentials")

    scheme, _, token = header.partition(" ")
    if scheme != "Bearer" or not token:
        raise AuthError(400, "malformed authorization header")

    try:
        payload_b64, signature_b64 = token.split(".")
        payload = _b64decode(payload_b64)
        signature = _b64decode(signature_b64)
    except (ValueError, TypeError):
        raise AuthError(400, "malformed token") from None

    if not _signature_valid(payload, signature):
        raise AuthError(401, "bad signature")

    claims = json.loads(payload)
    now = time.time()
    if claims["exp"] + CLOCK_SKEW_SECONDS < now:
        raise AuthError(401, "token expired")
    if claims.get("nbf", 0) - CLOCK_SKEW_SECONDS > now:
        raise AuthError(401, "token not yet valid")

    return Principal(user_id=claims["sub"], scopes=tuple(claims.get("scopes", ())))


def require_auth(*scopes):
    """Decorator for request handlers: authenticate, then enforce required scopes."""

    def decorator(handler):
        def wrapped(request):
            principal = authenticate(request.headers)
            missing = [scope for scope in scopes if scope not in principal.scopes]
            if missing:
                raise AuthError(403, f"missing scopes: {', '.join(missing)}")
            request.principal = principal
            return handler(request)

        wrapped.__name__ = handler.__name__
        return wrapped

    return decorator


@require_auth("orders:read")
def get_order(request):
    return {"id": request.path_params["id"], "owner": request.principal.user_id}


@require_auth("orders:read", "orders:write")
def cancel_order(request):
    return {"id": request.path_params["id"], "status": "cancelled"}
