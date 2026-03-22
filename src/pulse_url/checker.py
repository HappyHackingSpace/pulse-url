from dataclasses import dataclass
from enum import Enum

import httpx


class Status(Enum):
    OK = "OK"
    PROBLEM = "PROBLEM"
    UNREACHABLE = "UNREACHABLE"


@dataclass(frozen=True)
class CheckResult:
    status: Status
    status_code: int | None
    reason: str
    elapsed_ms: int


def check_url(
    url: str,
    timeout: float = 5.0,
    token: str | None = None,
) -> CheckResult:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = httpx.get(
            url,
            headers=headers,
            timeout=timeout,
            follow_redirects=False,
        )
        elapsed_ms = int(response.elapsed.total_seconds() * 1000)

        if 200 <= response.status_code < 300:
            return CheckResult(
                status=Status.OK,
                status_code=response.status_code,
                reason=response.reason_phrase,
                elapsed_ms=elapsed_ms,
            )

        return CheckResult(
            status=Status.PROBLEM,
            status_code=response.status_code,
            reason=response.reason_phrase,
            elapsed_ms=elapsed_ms,
        )

    except httpx.TimeoutException:
        return CheckResult(
            status=Status.UNREACHABLE,
            status_code=None,
            reason=f"TIMEOUT (after {timeout:.0f}s)",
            elapsed_ms=int(timeout * 1000),
        )
    except httpx.HTTPError:
        return CheckResult(
            status=Status.UNREACHABLE,
            status_code=None,
            reason="UNREACHABLE",
            elapsed_ms=0,
        )
