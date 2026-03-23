"""Bright Data billing adapter (``TODO.md`` Phase 6.4)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import httpx

from api_spend.models import SpendRecord
from api_spend.providers.brightdata import (
    BrightDataBillingProvider,
    brightdata_options_from_config,
)


def test_fetch_costs_normalizes_records():
    start, end = date(2025, 3, 10), date(2025, 3, 14)
    zone = "web_unlocker1"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert "/zone/cost" in str(request.url)
        assert request.headers.get("Authorization") == "Bearer token-1"
        q = request.url.params
        assert q.get("zone") == zone
        assert q.get("from") == "2025-03-10T00:00:00.000Z"
        assert q.get("to") == "2025-03-14T00:00:00.000Z"
        return httpx.Response(
            200,
            json={
                zone: {
                    "back_d0": {"cost": 1.5, "bw": 0},
                    "back_d1": {"cost": 2, "bw": 0},
                    "back_d2": {"cost": 0.25, "bw": 0},
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="token-1", zone=zone, client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    # anchor = end - 1d = Mar 13; back_d0 Mar 13, back_d1 Mar 12, back_d2 Mar 11
    assert r.records == [
        SpendRecord(
            provider="brightdata",
            service="web_unlocker1:back_d2",
            date=date(2025, 3, 11),
            amount=Decimal("0.25"),
            currency="USD",
        ),
        SpendRecord(
            provider="brightdata",
            service="web_unlocker1:back_d1",
            date=date(2025, 3, 12),
            amount=Decimal("2"),
            currency="USD",
        ),
        SpendRecord(
            provider="brightdata",
            service="web_unlocker1:back_d0",
            date=date(2025, 3, 13),
            amount=Decimal("1.5"),
            currency="USD",
        ),
    ]


def test_fetch_costs_wrapped_zone_payload():
    start, end = date(2025, 1, 1), date(2025, 1, 3)
    zone = "z1"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"some_id": {"back_d0": {"cost": 10}, "back_d1": {"cost": 1}}},
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone=zone, client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert len(r.records) == 2
    assert all(rec.service.startswith("z1:back_d") for rec in r.records)


def test_fetch_costs_empty_zone_returns_error():
    transport = httpx.MockTransport(lambda r: httpx.Response(500))
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="  ", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert r.records == []
    assert "zone" in (r.error or "").lower()


def test_fetch_costs_api_error_returns_empty_and_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "unauthorized"})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="bad", zone="z", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert r.records == []
    assert r.error is not None
    assert "401" in r.error


def test_validate_credentials_requires_zone():
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="", client=http)
        assert p.validate_credentials() is False


def test_validate_credentials_true():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"z": {"back_d0": {"cost": 0}}})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="z", client=http)
        assert p.validate_credentials() is True


def test_brightdata_options_from_config():
    assert brightdata_options_from_config({}) == ""
    assert brightdata_options_from_config({"zone": " my_zone "}) == "my_zone"
