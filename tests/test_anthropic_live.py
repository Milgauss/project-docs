"""Live Anthropic cost report checks — opt-in (real network, admin key).

Run from the **repository root** (folder with ``pyproject.toml`` and ``tests/``), after ``pip install -e ".[dev]"``::

    cd /path/to/api-spend
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    export API_SPEND_LIVE_TESTS=1
    export API_SPEND_ANTHROPIC_API_KEY='sk-ant-admin-...'
    pytest tests/test_anthropic_live.py -v

Optional: write normalized fetch results as JSON::

    cd /path/to/api-spend
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    export API_SPEND_LIVE_TESTS=1
    export API_SPEND_ANTHROPIC_API_KEY='sk-ant-admin-...'
    export API_SPEND_LIVE_DUMP_PATH=./anthropic_live_costs.json
    pytest tests/test_anthropic_live.py -v

Use an **Anthropic admin API key** (``sk-ant-admin…``), not a standard API key.

Same env var as OpenAI live tests: ``API_SPEND_LIVE_TESTS`` and ``API_SPEND_LIVE_DUMP_PATH``.

Debug: ``API_SPEND_ANTHROPIC_RAW_RESPONSE_PATH`` → file, ``stdout`` / ``-``, or ``stderr`` (see README).
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from api_spend.providers.anthropic import AnthropicBillingProvider

_LIVE = os.environ.get("API_SPEND_LIVE_TESTS", "").strip().lower() in (
    "1",
    "true",
    "yes",
)
_KEY = os.environ.get("API_SPEND_ANTHROPIC_API_KEY", "").strip()

_SKIP = pytest.mark.skipif(
    not (_LIVE and _KEY),
    reason=(
        "Set API_SPEND_LIVE_TESTS=1 and API_SPEND_ANTHROPIC_API_KEY "
        "(see module docstring)"
    ),
)


@_SKIP
def test_live_anthropic_validate_credentials():
    with AnthropicBillingProvider(api_key=_KEY) as p:
        ok = p.validate_credentials()
    assert ok is True, (
        "cost_report probe failed — use an admin API key (sk-ant-admin…)"
    )


@_SKIP
def test_live_anthropic_fetch_costs_recent_window():
    """Accept empty ``records`` (no spend in window); when present, assert normalized shape."""
    end = date.today()
    start = end - timedelta(days=3)
    with AnthropicBillingProvider(api_key=_KEY) as p:
        r = p.fetch_costs(start, end)
    assert r.error is None, f"fetch_costs error: {r.error}"
    assert isinstance(r.records, list)

    keys: list[tuple[date, str]] = []
    for rec in r.records:
        assert rec.provider == "anthropic"
        assert rec.currency == "USD"
        assert start <= rec.date < end
        assert isinstance(rec.amount, Decimal)
        assert rec.amount >= 0, f"unexpected negative amount: {rec.amount!r}"
        assert rec.service.strip() != "", "service must be non-empty after normalization"
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
