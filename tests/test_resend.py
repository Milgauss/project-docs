"""Resend snapshot adapter (mocked HTTP)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import httpx
import pytest

from api_spend.providers.resend import ResendSnapshotProvider


def _resp(quota_month: str | None = None, quota_day: str | None = None) -> httpx.Response:
    h: dict[str, str] = {}
    if quota_month is not None:
        h["x-resend-monthly-quota"] = quota_month
    if quota_day is not None:
        h["x-resend-daily-quota"] = quota_day
    return httpx.Response(200, json={"object": "list", "data": []}, headers=h)


def test_read_counter_prefers_monthly_over_daily():
    def handler(request: httpx.Request) -> httpx.Response:
        return _resp(quota_month="10", quota_day="99")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = ResendSnapshotProvider("re_x", client=http)
        assert p.read_counter() == 10
        assert p.sync_quota_period(datetime(2025, 1, 1, tzinfo=timezone.utc)) == "2025-01"


def test_read_counter_falls_back_to_daily_quota():
    def handler(request: httpx.Request) -> httpx.Response:
        return _resp(quota_month=None, quota_day="42")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = ResendSnapshotProvider("re_x", client=http)
        assert p.read_counter() == 42
        assert p.sync_quota_period(datetime(2025, 3, 22, 15, 0, 0, tzinfo=timezone.utc)) == "2025-03-22"


_MARCH_2025 = datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_read_counter_list_fallback_counts_current_utc_month():
    """When quota headers are absent, paginate list and count created_at in UTC month."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("limit") == "100"
        return httpx.Response(
            200,
            headers={},
            json={
                "object": "list",
                "has_more": False,
                "data": [
                    {
                        "id": "a",
                        "created_at": "2025-03-20T10:00:00.000000+00:00",
                    },
                    {
                        "id": "b",
                        "created_at": "2025-03-01T08:00:00.000000+00:00",
                    },
                    {
                        "id": "c",
                        "created_at": "2025-02-28T12:00:00.000000+00:00",
                    },
                ],
            },
        )

    fixed = _MARCH_2025
    with (
        patch("api_spend.providers.resend._now_utc", return_value=fixed),
        httpx.Client(transport=httpx.MockTransport(handler)) as http,
    ):
        p = ResendSnapshotProvider("re_x", client=http)
        assert p.read_counter() == 2
        assert p.sync_quota_period(fixed) == "2025-03"


def test_read_counter_list_fallback_second_page():
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        after = request.url.params.get("after")
        calls.append(str(after or ""))
        if after is None:
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "has_more": True,
                    "data": [
                        {
                            "id": "p1-new",
                            "created_at": "2025-03-25T10:00:00+00:00",
                        },
                        {
                            "id": "p1-old",
                            "created_at": "2025-03-02T10:00:00+00:00",
                        },
                    ],
                },
            )
        assert after == "p1-old"
        return httpx.Response(
            200,
            json={
                "object": "list",
                "has_more": False,
                "data": [
                    {
                        "id": "p2",
                        "created_at": "2025-02-10T10:00:00+00:00",
                    },
                ],
            },
        )

    fixed = _MARCH_2025
    with (
        patch("api_spend.providers.resend._now_utc", return_value=fixed),
        patch("api_spend.providers.resend.time.sleep", lambda _s: None),
        httpx.Client(transport=httpx.MockTransport(handler)) as http,
    ):
        p = ResendSnapshotProvider("re_x", client=http)
        assert p.read_counter() == 2
        assert calls == ["", "p1-old"]


def test_estimate_cost_pro():
    with httpx.Client(transport=httpx.MockTransport(lambda r: _resp("0"))) as http:
        p = ResendSnapshotProvider("re_x", plan="pro", client=http)
        assert p.estimate_cost(100) == Decimal("0.04")


def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown resend plan"):
        ResendSnapshotProvider("re_x", plan="enterprise")


def test_validate_credentials_false_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "nope"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = ResendSnapshotProvider("re_bad", client=http)
        assert p.validate_credentials() is False


def test_provider_registry():
    from api_spend.providers import PROVIDER_REGISTRY

    assert PROVIDER_REGISTRY["resend"] is ResendSnapshotProvider
