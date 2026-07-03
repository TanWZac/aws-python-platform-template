from contextvars import ContextVar, Token

_correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")


def get_correlation_id() -> str:
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> Token[str]:
    return _correlation_id_ctx.set(correlation_id)


def reset_correlation_id(token: Token[str]) -> None:
    _correlation_id_ctx.reset(token)