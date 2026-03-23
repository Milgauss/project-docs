"""Live Resend snapshot checks — opt-in (real network, API key).

Run from the **repository root** after ``pip install -e ".[dev]"``::

    cd /path/to/api-spend
    source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
    export API_SPEND_LIVE_TESTS=1
    export API_SPEND_RESEND_API_KEY='re_...'
    export API_SPEND_RESEND_PLAN='pro'
    pytest tests/test_resend_live.py -v

Optional dump / raw::

    export API_SPEND_LIVE_DUMP_PATH=./resend_live_snapshot.json
    export API_SPEND_RESEND_RAW_RESPONSE_PATH=./resend_raw_response.json

``API_SPEND_RESEND_PLAN`` defaults to ``pro`` if unset. Resend may return only
``x-resend-daily-quota`` (free tier); the adapter falls back and uses UTC **day** snapshot periods.
If neither quota header is present (only ``ratelimit-*`` request throttling), the adapter **paginates**
``GET /emails`` and counts rows in the **current UTC month** (see ``ResendSnapshotProvider`` docstring).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from api_spend.providers.resend import ResendSnapshotProvider
from api_spend.snapshot_sync import run_snapshot_sync
from api_spend.store import SpendStore

_LIVE = os.environ.get("API_SPEND_LIVE_TESTS", "").strip().lower() in (
    "1",
    "true",
    "yes",
)
_KEY = os.environ.get("API_SPEND_RESEND_API_KEY", "").strip()
_PLAN = os.environ.get("API_SPEND_RESEND_PLAN", "pro").strip() or "pro"

_SKIP = pytest.mark.skipif(
    not (_LIVE and _KEY),
    reason="Set API_SPEND_LIVE_TESTS=1 and API_SPEND_RESEND_API_KEY (see module docstring)",
)


def _dump_snapshot_runs(path: Path, runs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"runs": runs}, indent=2) + "\n", encoding="utf-8")


@_SKIP
def test_live_resend_read_counter():
    """Surfaces HTTP / missing-header errors (not swallowed)."""
    with ResendSnapshotProvider(_KEY, plan=_PLAN) as p:
        try:
            n = p.read_counter()
        except Exception as e:
            pytest.fail(
                "Resend GET /emails failed. If the key is valid, capture "
                "API_SPEND_RESEND_RAW_RESPONSE_PATH. Expected quota headers "
                "(x-resend-monthly-quota / x-resend-daily-quota) or a list fallback "
                "(object=list with created_at on each row). "
                f"Cause: {e!r}"
            )
        assert isinstance(n, int) and n >= 0, f"unexpected counter: {n!r}"


@_SKIP
def test_live_resend_snapshot_sync_twice():
    store = SpendStore.open(":memory:")
    runs: list[dict] = []
    with ResendSnapshotProvider(_KEY, plan=_PLAN) as p:
        t0 = datetime.now(timezone.utc)
        r0 = run_snapshot_sync(store, "resend", "emails", p, t0)
        assert r0.error is None, r0.error
        assert r0.counter_observed is not None
        assert r0.records == []
        time.sleep(0.05)
        t1 = datetime.now(timezone.utc)
        r1 = run_snapshot_sync(store, "resend", "emails", p, t1)
        assert r1.error is None, r1.error
        assert r1.counter_observed is not None

        runs.append(
            {
                "recorded_at": t0.isoformat(),
                "counter_observed": r0.counter_observed,
                "error": r0.error,
                "records": [rec.model_dump(mode="json") for rec in r0.records],
            }
        )
        runs.append(
            {
                "recorded_at": t1.isoformat(),
                "counter_observed": r1.counter_observed,
                "error": r1.error,
                "records": [rec.model_dump(mode="json") for rec in r1.records],
            }
        )

        for rec in r1.records:
            assert rec.provider == "resend"
            assert rec.service == "emails"
            assert rec.currency == "USD"
            assert isinstance(rec.amount, Decimal)
            assert rec.amount >= 0

    dump_path = os.environ.get("API_SPEND_LIVE_DUMP_PATH", "").strip()
    if dump_path:
        _dump_snapshot_runs(Path(dump_path).expanduser().resolve(), runs)
