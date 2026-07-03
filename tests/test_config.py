from platform_service.core.config import Settings


def test_docs_enabled_default_true_only_for_local() -> None:
    local_settings = Settings(_env_file=None, APP_ENV="local")
    prod_settings = Settings(_env_file=None, APP_ENV="prod")

    assert local_settings.docs_enabled is True
    assert prod_settings.docs_enabled is False


def test_authentication_enabled_default_for_non_local() -> None:
    local_settings = Settings(_env_file=None, APP_ENV="local")
    prod_settings = Settings(_env_file=None, APP_ENV="prod")

    assert local_settings.authentication_enabled is False
    assert prod_settings.authentication_enabled is True


def test_explicit_auth_and_docs_overrides() -> None:
    settings = Settings(
        _env_file=None,
        APP_ENV="prod",
        AUTH_ENABLED=False,
        ENABLE_DOCS=True,
    )

    assert settings.authentication_enabled is False
    assert settings.docs_enabled is True