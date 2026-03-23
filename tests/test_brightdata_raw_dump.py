"""``API_SPEND_BRIGHTDATA_RAW_RESPONSE_PATH`` debug output."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from api_spend.http_raw_dump import BRIGHTDATA_RAW_RESPONSE_ENV
from api_spend.providers.brightdata import BrightDataBillingProvider


def test_fetch_costs_writes_raw_envelope_to_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "bd_raw.json"
    monkeypatch.setenv(BRIGHTDATA_RAW_RESPONSE_ENV, str(raw_path))

    payload = {"zone_x": {"back_d0": {"cost": 1.0, "bw": 0}}}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="zone_x", client=http)
        r = p.fetch_costs(date(2025, 1, 1), date(2025, 1, 3))

    assert r.error is None
    assert raw_path.is_file()
    outer = json.loads(raw_path.read_text(encoding="utf-8"))
    assert outer["http_status"] == 200
    assert "zone/cost" in outer["url"]
    assert outer["json"] == payload


def test_validate_appends_second_raw_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "bd_raw.json"
    monkeypatch.setenv(BRIGHTDATA_RAW_RESPONSE_ENV, str(raw_path))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"z": {"back_d0": {"cost": 0}}})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="z", client=http)
        assert p.validate_credentials() is True
        p.fetch_costs(date(2025, 2, 1), date(2025, 2, 2))

    text = raw_path.read_text(encoding="utf-8")
    assert "\n---\n" in text
    parts = text.split("\n---\n")
    assert len(parts) == 2
    assert json.loads(parts[0])["http_status"] == 200
    assert json.loads(parts[1])["http_status"] == 200


def test_raw_dump_skipped_without_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(BRIGHTDATA_RAW_RESPONSE_ENV, raising=False)

    raw_path = tmp_path / "missing.json"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http:
        p = BrightDataBillingProvider(api_key="k", zone="z", client=http)
        p.fetch_costs(date(2025, 1, 1), date(2025, 1, 2))

    assert not raw_path.exists()
