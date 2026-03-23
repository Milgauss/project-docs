"""Bright Data monthly ``back_mN`` buckets (API often omits or zeroes ``back_dN``)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import httpx

from api_spend.models import SpendRecord
from api_spend.providers.brightdata import BrightDataBillingProvider


def test_fetch_costs_monthly_only_payload():
    """When the API returns only ``back_mN``, attribute to the first day of that month."""
    start, end = date(2025, 3, 10), date(2025, 3, 20)
    zone = "my_zone"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                zone: {
                    "back_m1": {"cost": 0, "bw": 0},
                    "back_m0": {"cost": 12.34, "bw": 0},
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone=zone, client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert r.records == [
        SpendRecord(
            provider="brightdata",
            service="my_zone:back_m0",
            date=date(2025, 3, 1),
            amount=Decimal("12.34"),
            currency="USD",
        ),
    ]


def test_fetch_costs_daily_zero_monthly_nonzero_uses_monthly():
    start, end = date(2025, 3, 10), date(2025, 3, 14)
    zone = "z"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                zone: {
                    "back_d0": {"cost": 0, "bw": 1},
                    "back_d1": {"cost": 0, "bw": 1},
                    "back_m0": {"cost": 5, "bw": 0},
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone=zone, client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert len(r.records) == 1
    assert r.records[0].service == "z:back_m0"
    assert r.records[0].amount == Decimal("5")


def test_fetch_costs_daily_nonzero_ignores_monthly_for_output():
    start, end = date(2025, 3, 10), date(2025, 3, 14)
    zone = "z"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                zone: {
                    "back_d0": {"cost": 0.5, "bw": 0},
                    "back_m0": {"cost": 999, "bw": 0},
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone=zone, client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert len(r.records) == 1
    assert r.records[0].service == "z:back_d0"
