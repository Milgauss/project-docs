"""Anthropic billing adapter (``TODO.md`` Phase 6.2)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import httpx

from api_spend.models import SpendRecord
from api_spend.providers.anthropic import AnthropicBillingProvider


def test_fetch_costs_normalizes_records():
    start, end = date(2025, 1, 1), date(2025, 1, 4)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert "/v1/organizations/cost_report" in str(request.url)
        assert request.headers.get("x-api-key") == "sk-ant-admin-test"
        assert request.headers.get("anthropic-version") == "2023-06-01"
        assert set(request.url.params.get_list("group_by[]")) == {
            "workspace_id",
            "description",
        }
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "starting_at": "2025-01-01T00:00:00Z",
                        "results": [
                            {
                                "workspace_id": "ws_1",
                                "model": "claude-3-5-sonnet",
                                "cost_type": "usage",
                                "token_type": "input",
                                "amount": 123,
                                "currency": "USD",
                            }
                        ],
                    },
                    {
                        "starting_at": "2025-01-02T00:00:00Z",
                        "results": [
                            {
                                "description": "Other line",
                                "amount": 50,
                                "currency": "USD",
                            }
                        ],
                    },
                ],
                "has_more": False,
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-test", client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert r.records == [
        SpendRecord(
            provider="anthropic",
            service="ws_1:claude-3-5-sonnet:usage:input",
            date=date(2025, 1, 1),
            amount=Decimal("1.23"),
            currency="USD",
        ),
        SpendRecord(
            provider="anthropic",
            service="other line",
            date=date(2025, 1, 2),
            amount=Decimal("0.5"),
            currency="USD",
        ),
    ]


def test_fetch_costs_pagination():
    start, end = date(2025, 2, 1), date(2025, 2, 3)
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
                            "starting_at": "2025-02-01T00:00:00Z",
                            "results": [
                                {
                                    "description": "a",
                                    "amount": 100,
                                    "currency": "USD",
                                }
                            ],
                        }
                    ],
                    "has_more": True,
                    "next_page": "p2",
                },
            )
        assert "page=p2" in str(request.url) or request.url.params.get("page") == "p2"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "starting_at": "2025-02-02T00:00:00Z",
                        "results": [
                            {
                                "description": "b",
                                "amount": 200,
                                "currency": "USD",
                            }
                        ],
                    }
                ],
                "has_more": False,
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-test", client=http)
        r = p.fetch_costs(start, end)
    assert r.error is None
    assert n == 2
    assert {rec.service for rec in r.records} == {"a", "b"}


def test_fetch_costs_http_error_returns_empty_and_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": {"type": "authentication_error", "message": "bad"}},
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-x", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert r.records == []
    assert r.error is not None
    assert "401" in r.error
    assert "bad" in r.error


def test_fetch_costs_non_admin_key_no_http():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"data": [], "has_more": False})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-api03-not-admin", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))
    assert calls == []
    assert r.records == []
    assert "admin" in (r.error or "").lower()


def test_validate_credentials_false_without_admin_prefix():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no HTTP when key is not sk-ant-admin")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-api03-xxx", client=http)
        assert p.validate_credentials() is False


def test_validate_credentials_true():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [], "has_more": False})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-ok", client=http)
        assert p.validate_credentials() is True


def test_validate_credentials_false_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": {"message": "nope"}})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-x", client=http)
        assert p.validate_credentials() is False
