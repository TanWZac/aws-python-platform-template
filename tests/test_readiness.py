import pytest
import httpx
import respx

from platform_service.core.readiness import evaluate_readiness


class TestEvaluateReadiness:
    async def test_returns_ready_with_no_urls(self) -> None:
        result = await evaluate_readiness([], timeout_seconds=1.0)

        assert result["status"] == "ready"
        assert result["dependencies"] == []

    @respx.mock
    async def test_returns_ready_when_all_dependencies_healthy(self) -> None:
        respx.get("http://service-a/health").mock(return_value=httpx.Response(200))
        respx.get("http://service-b/health").mock(return_value=httpx.Response(204))

        result = await evaluate_readiness(
            ["http://service-a/health", "http://service-b/health"],
            timeout_seconds=1.0,
        )

        assert result["status"] == "ready"
        assert all(d["status"] == "ready" for d in result["dependencies"])

    @respx.mock
    async def test_returns_not_ready_when_dependency_returns_5xx(self) -> None:
        respx.get("http://service-a/health").mock(return_value=httpx.Response(503))

        result = await evaluate_readiness(["http://service-a/health"], timeout_seconds=1.0)

        assert result["status"] == "not_ready"
        assert result["dependencies"][0]["status"] == "not_ready"
        assert result["dependencies"][0]["status_code"] == 503

    @respx.mock
    async def test_returns_not_ready_on_connection_error(self) -> None:
        respx.get("http://unreachable/health").mock(side_effect=httpx.ConnectError("refused"))

        result = await evaluate_readiness(["http://unreachable/health"], timeout_seconds=1.0)

        assert result["status"] == "not_ready"
        assert result["dependencies"][0]["status"] == "not_ready"
        assert result["dependencies"][0]["status_code"] == 0

    @respx.mock
    async def test_one_failing_dependency_marks_whole_check_not_ready(self) -> None:
        respx.get("http://ok/health").mock(return_value=httpx.Response(200))
        respx.get("http://down/health").mock(return_value=httpx.Response(500))

        result = await evaluate_readiness(
            ["http://ok/health", "http://down/health"],
            timeout_seconds=1.0,
        )

        assert result["status"] == "not_ready"
        statuses = {d["target"]: d["status"] for d in result["dependencies"]}
        assert statuses["http://ok/health"] == "ready"
        assert statuses["http://down/health"] == "not_ready"

    @respx.mock
    async def test_includes_status_code_in_dependency_result(self) -> None:
        respx.get("http://service/health").mock(return_value=httpx.Response(200))

        result = await evaluate_readiness(["http://service/health"], timeout_seconds=1.0)

        assert result["dependencies"][0]["status_code"] == 200

    async def test_real_timeout_marks_dependency_not_ready(self) -> None:
        """Uses a real unreachable address to verify timeout handling."""
        result = await evaluate_readiness(
            ["http://127.0.0.1:9/unreachable"],
            timeout_seconds=0.05,
        )

        assert result["status"] == "not_ready"
        assert result["dependencies"][0]["status"] == "not_ready"
