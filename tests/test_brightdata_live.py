"""Live Bright Data zone cost checks — opt-in (real network, API key + zone).

Run from the **repository root** (folder with ``pyproject.toml`` and ``tests/``), after ``pip install -e ".[dev]"``::

    cd /path/to/api-spend
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    export API_SPEND_LIVE_TESTS=1
    export API_SPEND_BRIGHTDATA_API_KEY='...'
    export API_SPEND_BRIGHTDATA_ZONE='your_zone_name'
    pytest tests/test_brightdata_live.py -v

Optional: write normalized fetch results as JSON::

    cd /path/to/api-spend
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    export API_SPEND_LIVE_TESTS=1
    export API_SPEND_BRIGHTDATA_API_KEY='...'
    export API_SPEND_BRIGHTDATA_ZONE='your_zone_name'
    export API_SPEND_LIVE_DUMP_PATH=./brightdata_live_costs.json
    pytest tests/test_brightdata_live.py -v

``API_SPEND_BRIGHTDATA_ZONE`` is **only** for this test harness; normal use sets
``options.zone`` in YAML (``PLANNED_INTERFACE.md`` §3.1).

Same flags as other live tests: ``API_SPEND_LIVE_TESTS`` and ``API_SPEND_LIVE_DUMP_PATH``.

Debug: ``API_SPEND_BRIGHTDATA_RAW_RESPONSE_PATH`` (same behavior as OpenAI/Anthropic raw vars; see README *Raw API responses*).
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from api_spend.providers.brightdata import BrightDataBillingProvider

_LIVE = os.environ.get("API_SPEND_LIVE_TESTS", "").strip().lower() in (
    "1",
    "true",
    "yes",
)
_KEY = os.environ.get("API_SPEND_BRIGHTDATA_API_KEY", "").strip()
_ZONE = os.environ.get("API_SPEND_BRIGHTDATA_ZONE", "").strip()
_ZONE_LOWER = _ZONE.lower()

_SERVICE_BUCKET = re.compile(r"^[^:]+:(?:back_d\d+|back_m\d+|custom)$")

_SKIP = pytest.mark.skipif(
    not (_LIVE and _KEY and _ZONE),
    reason=(
        "Set API_SPEND_LIVE_TESTS=1, API_SPEND_BRIGHTDATA_API_KEY, and "
        "API_SPEND_BRIGHTDATA_ZONE (see module docstring)"
    ),
)


@_SKIP
def test_live_brightdata_validate_credentials():
    with BrightDataBillingProvider(api_key=_KEY, zone=_ZONE) as p:
        ok = p.validate_credentials()
    assert ok is True, (
        "zone/cost probe failed — check API key, zone name, and account access"
    )


@_SKIP
def test_live_brightdata_fetch_costs_recent_window():
    """Accept empty ``records`` (no cost in window); when present, assert normalized shape."""
    end = date.today()
    start = end - timedelta(days=3)
    with BrightDataBillingProvider(api_key=_KEY, zone=_ZONE) as p:
        r = p.fetch_costs(start, end)
    assert r.error is None, f"fetch_costs error: {r.error}"
    assert isinstance(r.records, list)

    keys: list[tuple[date, str]] = []
    for rec in r.records:
        assert rec.provider == "brightdata"
        assert rec.currency == "USD"
        assert start <= rec.date < end
        assert isinstance(rec.amount, Decimal)
        assert rec.amount >= 0, f"unexpected negative amount: {rec.amount!r}"
        assert rec.service.strip() != "", "service must be non-empty after normalization"
        assert rec.service.startswith(
            f"{_ZONE_LOWER}:"
        ), f"service should start with lowercased zone prefix: {rec.service!r}"
        assert _SERVICE_BUCKET.match(
            rec.service
        ), f"service should be {{zone}}:back_dN, back_mN, or custom: {rec.service!r}"
        keys.append((rec.date, rec.service))

    assert len(keys) == len(set(keys)), (
        "duplicate (date, service) — adapter should merge into one SpendRecord"
    )

    dump_path = os.environ.get("API_SPEND_LIVE_DUMP_PATH", "").strip()
    if dump_path:
        out = Path(dump_path).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "range": {"start": start.isoformat(), "end": end.isoformat()},
            "record_count": len(r.records),
            "records": [rec.model_dump(mode="json") for rec in r.records],
        }
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
