from collections.abc import Sequence
from typing import Any

import httpx


async def evaluate_readiness(
    dependency_urls: Sequence[str],
    timeout_seconds: float,
) -> dict[str, Any]:
    checks: list[dict[str, str | int]] = []
    ready = True

    if not dependency_urls:
        return {
            "status": "ready",
            "dependencies": checks,
        }

    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        for dependency_url in dependency_urls:
            try:
                response = await client.get(dependency_url)
                check_ready = response.status_code < 400
                checks.append(
                    {
                        "target": dependency_url,
                        "status": "ready" if check_ready else "not_ready",
                        "status_code": response.status_code,
                    }
                )
                ready = ready and check_ready
            except httpx.HTTPError:
                checks.append(
                    {
                        "target": dependency_url,
                        "status": "not_ready",
                        "status_code": 0,
                    }
                )
                ready = False

    return {
        "status": "ready" if ready else "not_ready",
        "dependencies": checks,
    }