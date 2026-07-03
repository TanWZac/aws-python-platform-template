from typing import Annotated
import hmac

from fastapi import Header, Request

from platform_service.core.config import settings
from platform_service.core.errors import AppError


def _constant_time_key_match(candidate: str, allowed_keys: set[str]) -> bool:
    """Compare candidate against every allowed key in constant time to prevent
    timing-based key enumeration attacks."""
    matched = False
    for key in allowed_keys:
        if hmac.compare_digest(candidate, key):
            matched = True
    return matched


def require_api_key(
    request: Request,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if not settings.authentication_enabled:
        request.state.principal = "anonymous"
        return

    allowed_keys = settings.api_keys_set
    if not allowed_keys:
        raise AppError(
            code="auth_not_configured",
            message="Authentication is enabled but API_KEYS is not configured.",
            status_code=500,
        )

    if not x_api_key or not _constant_time_key_match(x_api_key, allowed_keys):
        raise AppError(
            code="unauthorized",
            message="Missing or invalid API key.",
            status_code=401,
        )

    request.state.principal = "api_key"