from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _package_version() -> str:
    try:
        from importlib.metadata import version
        return version("aws-python-platform-template")
    except Exception:  # pragma: no cover
        return "0.0.0"


class Settings(BaseSettings):
    app_name: str = Field(default="aws-python-platform-template", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_version: str = Field(default_factory=_package_version, alias="APP_VERSION")
    aws_region: str = Field(default="", alias="AWS_REGION")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_docs: bool | None = Field(default=None, alias="ENABLE_DOCS")
    auth_enabled: bool | None = Field(default=None, alias="AUTH_ENABLED")
    api_keys: str = Field(default="", alias="API_KEYS")
    cors_allow_origins: str = Field(default="", alias="CORS_ALLOW_ORIGINS")
    readiness_check_urls: str = Field(default="", alias="READINESS_CHECK_URLS")
    readiness_timeout_seconds: float = Field(default=1.5, alias="READINESS_TIMEOUT_SECONDS")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_ssl: bool = Field(default=False, alias="REDIS_SSL")
    redis_timeout_seconds: float = Field(default=2.0, alias="REDIS_TIMEOUT_SECONDS")
    cache_default_ttl_seconds: int = Field(default=300, alias="CACHE_DEFAULT_TTL_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @staticmethod
    def _split_csv(raw_value: str) -> list[str]:
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @property
    def docs_enabled(self) -> bool:
        if self.enable_docs is not None:
            return self.enable_docs
        return self.app_env == "local"

    @property
    def authentication_enabled(self) -> bool:
        if self.auth_enabled is not None:
            return self.auth_enabled
        return self.app_env != "local"

    @property
    def api_keys_set(self) -> set[str]:
        return set(self._split_csv(self.api_keys))

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return self._split_csv(self.cors_allow_origins)

    @property
    def readiness_check_urls_list(self) -> list[str]:
        return self._split_csv(self.readiness_check_urls)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
