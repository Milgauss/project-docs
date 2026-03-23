"""Bright Data ``custom`` bucket (some zones omit ``back_d`` / ``back_m``)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import httpx

from api_spend.models import SpendRecord
from api_spend.providers.brightdata import BrightDataBillingProvider


def test_fetch_costs_custom_shape_like_live_raw():
    """Shape from real API: internal id key wrapping ``custom`` with DD-MMM-YYYY range."""
    start, end = date(2026, 3, 19), date(2026, 3, 22)
    zone = "web_unlocker1"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hl_df349005": {
                    "custom": {
                        "cost": 0.027,
                        "bw": 992594,
                        "range": {
                            "from": "19-Mar-2026",
                            "to": "22-Mar-2026",
                        },
                        "reqs_unblocker": 18,
                    }
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
            service="web_unlocker1:custom",
            date=date(2026, 3, 19),
            amount=Decimal("0.027"),
            currency="USD",
        ),
    ]


def test_custom_zero_cost_still_emitted_when_no_back_buckets():
    start, end = date(2026, 3, 21), date(2026, 3, 22)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hl_x": {
                    "custom": {
                        "cost": 0,
                        "range": {"from": "21-Mar-2026", "to": "22-Mar-2026"},
                    }
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="z", client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert len(r.records) == 1
    assert r.records[0].amount == Decimal("0")
    assert r.records[0].service == "z:custom"
