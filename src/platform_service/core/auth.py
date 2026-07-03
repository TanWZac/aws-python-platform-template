from typing import Annotated

from fastapi import Header, Request

from platform_service.core.config import settings
from platform_service.core.errors import AppError


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

    if not x_api_key or x_api_key not in allowed_keys:
        raise AppError(
            code="unauthorized",
            message="Missing or invalid API key.",
            status_code=401,
        )

    request.state.principal = "api_key"