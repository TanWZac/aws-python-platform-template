from __future__ import annotations

from typing import Any

from platform_service.core.config import settings
from platform_service.core.errors import AppError

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover - imported only when boto3 is installed
    boto3 = None
    BotoCoreError = Exception
    ClientError = Exception


class SecretsManagerRepository:
    def __init__(self, client: Any | None = None) -> None:
        if client is not None:
            self.client: Any = client
            return

        if boto3 is None:
            self.client = None  # AppError raised on first use
            return

        client_kwargs: dict[str, str] = {}
        if settings.aws_region:
            client_kwargs["region_name"] = settings.aws_region

        self.client = boto3.client("secretsmanager", **client_kwargs)

    def _get_client(self) -> Any:
        if self.client is None:
            raise AppError(
                code="secrets_dependency_missing",
                message="boto3 is required to use AWS Secrets Manager integration.",
                status_code=500,
            )
        return self.client

    def get_secret_value(self, secret_id: str) -> str:
        try:
            result = self._get_client().get_secret_value(SecretId=secret_id)
        except (ClientError, BotoCoreError) as exc:
            raise AppError(
                code="secret_read_failed",
                message=f"Unable to read secret '{secret_id}'.",
                status_code=500,
            ) from exc

        secret_value = result.get("SecretString")
        if not secret_value:
            raise AppError(
                code="secret_empty",
                message=f"Secret '{secret_id}' is empty or binary.",
                status_code=500,
            )

        return secret_value