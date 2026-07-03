from unittest.mock import MagicMock, patch

import pytest

from platform_service.core.errors import AppError
from platform_service.repositories.secrets_manager_repository import SecretsManagerRepository


def _make_client(secret_string: str | None = "super-secret") -> MagicMock:
    """Return a mock boto3 secretsmanager client."""
    client = MagicMock()
    client.get_secret_value.return_value = {"SecretString": secret_string}
    return client


class TestSecretsManagerRepository:
    def test_returns_secret_string_on_success(self) -> None:
        repo = SecretsManagerRepository(client=_make_client("my-secret-value"))

        result = repo.get_secret_value("my-secret-id")

        assert result == "my-secret-value"

    def test_calls_secretsmanager_with_correct_secret_id(self) -> None:
        mock_client = _make_client("value")
        repo = SecretsManagerRepository(client=mock_client)

        repo.get_secret_value("prod/db/password")

        mock_client.get_secret_value.assert_called_once_with(SecretId="prod/db/password")

    def test_raises_app_error_on_client_error(self) -> None:
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}},
            "GetSecretValue",
        )
        repo = SecretsManagerRepository(client=mock_client)

        with pytest.raises(AppError) as exc_info:
            repo.get_secret_value("missing-secret")

        assert exc_info.value.code == "secret_read_failed"
        assert exc_info.value.status_code == 500

    def test_raises_app_error_on_botocore_error(self) -> None:
        from botocore.exceptions import BotoCoreError

        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = BotoCoreError()
        repo = SecretsManagerRepository(client=mock_client)

        with pytest.raises(AppError) as exc_info:
            repo.get_secret_value("any-secret")

        assert exc_info.value.code == "secret_read_failed"
        assert exc_info.value.status_code == 500

    def test_raises_app_error_when_secret_string_is_none(self) -> None:
        repo = SecretsManagerRepository(client=_make_client(secret_string=None))

        with pytest.raises(AppError) as exc_info:
            repo.get_secret_value("binary-secret")

        assert exc_info.value.code == "secret_empty"
        assert exc_info.value.status_code == 500

    def test_raises_app_error_when_secret_string_is_empty(self) -> None:
        repo = SecretsManagerRepository(client=_make_client(secret_string=""))

        with pytest.raises(AppError) as exc_info:
            repo.get_secret_value("empty-secret")

        assert exc_info.value.code == "secret_empty"

    def test_raises_app_error_when_boto3_unavailable(self) -> None:
        with patch(
            "platform_service.repositories.secrets_manager_repository.boto3",
            None,
        ):
            repo = SecretsManagerRepository()

        with pytest.raises(AppError) as exc_info:
            repo.get_secret_value("any-secret")

        assert exc_info.value.code == "secrets_dependency_missing"
        assert exc_info.value.status_code == 500

    def test_accepts_injected_client_skipping_boto3_init(self) -> None:
        """Passing a client at construction time should skip all boto3 logic."""
        mock_client = _make_client("injected-value")
        repo = SecretsManagerRepository(client=mock_client)

        result = repo.get_secret_value("test-secret")

        assert result == "injected-value"
