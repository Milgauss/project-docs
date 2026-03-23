"""OpenAI billing adapter (``TODO.md`` Phase 5.3)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import httpx

from api_spend.models import SpendRecord
from api_spend.providers.openai import OpenAIBillingProvider, _date_start_unix_utc, openai_options_from_config


def test_fetch_costs_normalizes_records():
    day = date(2025, 1, 15)
    ts = _date_start_unix_utc(day)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert "organization/costs" in str(request.url)
        assert request.headers.get("OpenAI-Organization") == "org-test"
        assert request.headers.get("Authorization", "").startswith("Bearer ")
        return httpx.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {
                        "object": "bucket",
                        "start_time": ts,
                        "end_time": ts + 86400,
                        "results": [
                            {
                                "object": "organization.costs.result",
                                "amount": {"value": 1.25, "currency": "usd"},
                                "line_item": "gpt-4o-mini, input",
                                "project_id": "proj_abc",
                            },
                            {
                                "object": "organization.costs.result",
                                "amount": {"value": 0.75, "currency": "usd"},
                                "line_item": "gpt-4o-mini, input",
                                "project_id": "proj_abc",
                            },
                        ],
                    }
                ],
                "next_page": None,
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(
            api_key="sk-test",
            organization_id="org-test",
            client=http,
        )
        r = p.fetch_costs(day, date(2025, 1, 16))
    assert r.error is None
    assert r.records == [
        SpendRecord(
            provider="openai",
            service="proj_abc:gpt-4o-mini, input",
            date=day,
            amount=Decimal("2"),
            currency="USD",
        )
    ]


def test_fetch_costs_pagination():
    d0, d1 = date(2025, 1, 1), date(2025, 1, 2)
    t0, t1 = _date_start_unix_utc(d0), _date_start_unix_utc(d1)
    n = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal n
        n += 1
        if n == 1:
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "start_time": t0,
                            "end_time": t0 + 86400,
                            "results": [
                                {
                                    "amount": {"value": 1, "currency": "usd"},
                                    "line_item": "a",
                                    "project_id": None,
                                }
                            ],
                        }
                    ],
                    "next_page": "cursor2",
                },
            )
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "start_time": t1,
                        "end_time": t1 + 86400,
                        "results": [
                            {
                                "amount": {"value": 3, "currency": "usd"},
                                "line_item": "b",
                                "project_id": None,
                            }
                        ],
                    }
                ],
                "next_page": None,
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(
            api_key="sk",
            organization_id="org-x",
            client=http,
        )
        r = p.fetch_costs(d0, date(2025, 1, 3))
    assert r.error is None
    assert {rec.service for rec in r.records} == {"a", "b"}
    assert sum(rec.amount for rec in r.records) == Decimal("4")
    assert n == 2


def test_fetch_costs_api_error_returns_empty_and_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": {"message": "invalid key", "type": "invalid_request_error"}},
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(
            api_key="bad",
            organization_id="org-x",
            client=http,
        )
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert r.records == []
    assert r.error is not None
    assert "401" in r.error
    assert "invalid key" in r.error


def test_fetch_costs_missing_organization_id():
    transport = httpx.MockTransport(lambda r: httpx.Response(500))
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(api_key="sk", organization_id="", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert r.records == []
    assert "organization_id" in (r.error or "")


def test_validate_credentials_true():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [], "next_page": None})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(
            api_key="sk",
            organization_id="org-x",
            client=http,
        )
        assert p.validate_credentials() is True


def test_validate_credentials_false_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": {"message": "forbidden"}})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(
            api_key="sk",
            organization_id="org-x",
            client=http,
        )
        assert p.validate_credentials() is False


def test_validate_credentials_false_without_org():
    transport = httpx.MockTransport(lambda r: httpx.Response(200))
    with httpx.Client(transport=transport) as http:
        p = OpenAIBillingProvider(api_key="sk", organization_id="", client=http)
        assert p.validate_credentials() is False


def test_openai_options_from_config():
    assert openai_options_from_config({}) == ""
    assert openai_options_from_config({"organization_id": " org-1 "}) == "org-1"


def test_service_unattributed_when_no_line_item():
    from api_spend.providers.openai import _parse_costs_buckets

    ts = int(datetime(2025, 2, 1, tzinfo=timezone.utc).timestamp())
    recs = _parse_costs_buckets(
        [
            {
                "start_time": ts,
                "end_time": ts + 86400,
                "results": [
                    {"amount": {"value": 0.5, "currency": "usd"}, "line_item": None, "project_id": None}
                ],
            }
        ]
    )
    assert len(recs) == 1
    assert recs[0].service == "unattributed"
