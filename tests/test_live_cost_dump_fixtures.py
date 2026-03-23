"""Sanitized JSON dumps matching ``API_SPEND_LIVE_DUMP_PATH`` output (see live tests).

Fixtures under ``tests/fixtures/`` are fake ids, dates, and amounts — not real API data.
They document the normalized ``SpendRecord`` shape after a successful live fetch.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pytest

from api_spend.models import SpendRecord

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_BRIGHTDATA_SERVICE = re.compile(r"^[^:]+:(?:back_d\d+|back_m\d+|custom)$")


def _load_dump(filename: str) -> dict:
    path = _FIXTURES / filename
    assert path.is_file(), f"missing fixture {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_dump_records(raw: dict, *, expected_provider: str) -> list[SpendRecord]:
    assert set(raw) == {"range", "record_count", "records"}
    rng = raw["range"]
    assert set(rng) == {"start", "end"}
    start = date.fromisoformat(rng["start"])
    end = date.fromisoformat(rng["end"])
    assert end > start, "range end must be after start (same semantics as fetch_costs [start, end))"

    rows = raw["records"]
    assert raw["record_count"] == len(rows), "record_count must match len(records)"

    out: list[SpendRecord] = []
    for row in rows:
        rec = SpendRecord.model_validate(row)
        assert rec.provider == expected_provider
        assert rec.currency == "USD"
        assert start <= rec.date < end
        assert rec.amount >= 0
        assert rec.service.strip() != ""
        out.append(rec)

    keys = [(r.date, r.service) for r in out]
    assert len(keys) == len(set(keys)), "duplicate (date, service) in dump"
    return out


def test_sanitized_openai_live_cost_dump_fixture():
    raw = _load_dump("openai_live_costs_sanitized.json")
    recs = _parse_dump_records(raw, expected_provider="openai")
    assert len(recs) >= 1
    assert all(":" in r.service for r in recs), "fixture mirrors project_id:line_item style"


def test_sanitized_anthropic_live_cost_dump_fixture():
    raw = _load_dump("anthropic_live_costs_sanitized.json")
    recs = _parse_dump_records(raw, expected_provider="anthropic")
    assert len(recs) >= 1
    assert all(":tokens:" in r.service for r in recs), (
        "fixture mirrors cost_report rows with model + cost_type + token_type"
    )


def test_sanitized_brightdata_live_cost_dump_fixture():
    raw = _load_dump("brightdata_live_costs_sanitized.json")
    recs = _parse_dump_records(raw, expected_provider="brightdata")
    assert len(recs) >= 1
    assert all(_BRIGHTDATA_SERVICE.match(r.service) for r in recs), (
        "fixture mirrors zone/cost back_dN → {zone}:back_dN"
    )


@pytest.mark.parametrize(
    "filename",
    [
        "openai_live_costs_sanitized.json",
        "anthropic_live_costs_sanitized.json",
        "brightdata_live_costs_sanitized.json",
    ],
)
def test_live_dump_fixtures_round_trip_model_dump_json(filename: str):
    """Same encoding path as live tests (``model_dump(mode='json')``)."""
    raw = _load_dump(filename)
    recs_in = [SpendRecord.model_validate(r) for r in raw["records"]]
    reencoded = [r.model_dump(mode="json") for r in recs_in]
    recs_out = [SpendRecord.model_validate(r) for r in reencoded]
    assert recs_in == recs_out
