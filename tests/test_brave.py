"""Brave Search snapshot adapter (mocked HTTP)."""

from __future__ import annotations

from decimal import Decimal

import httpx

from api_spend.providers.brave import BraveSnapshotProvider


def test_read_counter_limit_minus_remaining():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
            headers={"X-RateLimit-Limit": "2000", "X-RateLimit-Remaining": "1850"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = BraveSnapshotProvider("BSA_x", client=http)
        assert p.read_counter() == 150


def test_read_counter_comma_separated_prefers_larger_limit():
    """Brave sends burst + monthly as comma-separated pairs (larger limit = monthly)."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
            headers={
                "X-RateLimit-Limit": "1, 15000",
                "X-RateLimit-Remaining": "1, 13500",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = BraveSnapshotProvider("BSA_x", client=http)
        assert p.read_counter() == 1500


def test_read_counter_comma_separated_uses_policy_window():
    """When limits are not ordered by size, pick the longest w= window."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
            headers={
                "X-RateLimit-Limit": "100, 50",
                "X-RateLimit-Remaining": "90, 40",
                "X-RateLimit-Policy": "100;w=1, 50;w=2592000",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = BraveSnapshotProvider("BSA_x", client=http)
        assert p.read_counter() == 10


def test_read_counter_skips_zero_limit_segment():
    """Some tiers report ``50, 0`` for limit; use the positive segment only."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
            headers={
                "X-RateLimit-Limit": "50, 0",
                "X-RateLimit-Remaining": "45, 0",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        p = BraveSnapshotProvider("BSA_x", client=http)
        assert p.read_counter() == 5


def test_estimate_cost():
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                200,
                json={},
                headers={"X-RateLimit-Limit": "1000", "X-RateLimit-Remaining": "500"},
            )
        )
    ) as http:
        p = BraveSnapshotProvider("BSA_x", client=http)
        assert p.estimate_cost(500) == Decimal("2.5")


def test_provider_registry():
    from api_spend.providers import PROVIDER_REGISTRY

    assert PROVIDER_REGISTRY["brave_search"] is BraveSnapshotProvider
