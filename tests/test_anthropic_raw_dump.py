"""``API_SPEND_ANTHROPIC_RAW_RESPONSE_PATH`` debug output."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from api_spend.http_raw_dump import ANTHROPIC_RAW_RESPONSE_ENV
from api_spend.providers.anthropic import AnthropicBillingProvider


def test_fetch_costs_writes_raw_envelope_to_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "ant_raw.json"
    monkeypatch.setenv(ANTHROPIC_RAW_RESPONSE_ENV, str(raw_path))

    payload = {"data": [], "has_more": False}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-x", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))

    assert r.error is None
    outer = json.loads(raw_path.read_text(encoding="utf-8"))
    assert outer["http_status"] == 200
    assert "cost_report" in outer["url"]
    assert outer["json"] == payload


def test_validate_appends_second_raw_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "ant_raw.json"
    monkeypatch.setenv(ANTHROPIC_RAW_RESPONSE_ENV, str(raw_path))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [], "has_more": False})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-x", client=http)
        assert p.validate_credentials() is True
        p.fetch_costs(date(2025, 2, 1), date(2025, 2, 2))

    text = raw_path.read_text(encoding="utf-8")
    assert "\n---\n" in text
    parts = text.split("\n---\n")
    assert len(parts) == 2


def test_raw_dump_skipped_without_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(ANTHROPIC_RAW_RESPONSE_ENV, raising=False)
    raw_path = tmp_path / "missing.json"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [], "has_more": False})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = AnthropicBillingProvider(api_key="sk-ant-admin-x", client=http)
        p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))

    assert not raw_path.exists()
