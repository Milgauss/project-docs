"""Brave Search snapshot adapter — Web Search API rate-limit headers (``PLANNED_INTERFACE.md`` section 3.2)."""

from __future__ import annotations

import re
from decimal import Decimal

import httpx

from api_spend.http_raw_dump import BRAVE_RAW_RESPONSE_ENV, maybe_dump_http_response
from api_spend.providers.base import SnapshotProvider

BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
DEFAULT_TIMEOUT = 60.0
_PER_REQUEST_USD = Decimal("0.005")


def _parse_comma_ints(val: str | None, header_name: str) -> list[int]:
    if val is None or not str(val).strip():
        raise ValueError(f"missing required response header {header_name!r}")
    parts = [p.strip() for p in str(val).split(",")]
    out: list[int] = []
    for p in parts:
        if not p:
            continue
        try:
            out.append(int(p, 10))
        except ValueError as exc:
            raise ValueError(
                f"invalid integer segment in {header_name!r}: {val!r}"
            ) from exc
    if not out:
        raise ValueError(f"empty value for response header {header_name!r}")
    return out


def _policy_window_seconds(policy_segment: str) -> int:
    m = re.search(r"w=(\d+)", policy_segment, flags=re.IGNORECASE)
    return int(m.group(1), 10) if m else 0


def _parse_policy_windows(policy: str | None) -> list[int] | None:
    if policy is None or not str(policy).strip():
        return None
    return [_policy_window_seconds(p) for p in str(policy).split(",")]


def _choose_rate_limit_index(limits: list[int], windows: list[int] | None) -> int:
    """Pick the window to use for *used this period* (prefer longest policy window, else largest limit)."""
    positive = [i for i, lim in enumerate(limits) if lim > 0]
    if not positive:
        raise ValueError("X-RateLimit-Limit has no positive segment")
    if windows is not None and len(windows) == len(limits):
        return max(positive, key=lambda i: (windows[i], limits[i]))
    return max(positive, key=lambda i: limits[i])


def _used_from_rate_limit_headers(headers: httpx.Headers) -> int:
    limits = _parse_comma_ints(
        headers.get("X-RateLimit-Limit"), "X-RateLimit-Limit"
    )
    remaining = _parse_comma_ints(
        headers.get("X-RateLimit-Remaining"), "X-RateLimit-Remaining"
    )
    if len(limits) != len(remaining):
        raise ValueError(
            "X-RateLimit-Limit and X-RateLimit-Remaining must have the same "
            f"number of comma-separated segments (got {len(limits)} vs {len(remaining)})"
        )
    windows = _parse_policy_windows(headers.get("X-RateLimit-Policy"))
    idx = _choose_rate_limit_index(limits, windows)
    return max(0, limits[idx] - remaining[idx])


class BraveSnapshotProvider(SnapshotProvider):
    """Uses ``X-RateLimit-Limit`` − ``X-RateLimit-Remaining`` as the used counter.

    Brave may send **comma-separated** values (burst + monthly, etc.), with optional
    ``X-RateLimit-Policy`` segments like ``1;w=1, 15000;w=2592000``. The adapter picks
    the window with the **largest** ``w=`` (reset interval) among segments with
    ``limit > 0``; if policy is absent, it uses the segment with the **largest** limit.
    """

    def __init__(
        self,
        api_key: str,
        *,
        client: httpx.Client | None = None,
        raw_response_env: str = BRAVE_RAW_RESPONSE_ENV,
    ) -> None:
        self._api_key = api_key.strip()
        self._raw_env = raw_response_env
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> BraveSnapshotProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def read_counter(self) -> int:
        r = self._client.get(
            BRAVE_WEB_SEARCH_URL,
            params={"q": "api", "count": 1},
            headers={"X-Subscription-Token": self._api_key},
        )
        maybe_dump_http_response(r, self._raw_env)
        r.raise_for_status()
        return _used_from_rate_limit_headers(r.headers)

    def estimate_cost(self, usage_delta: int) -> Decimal:
        return _PER_REQUEST_USD * usage_delta

    def validate_credentials(self) -> bool:
        try:
            self.read_counter()
            return True
        except Exception:
            return False
