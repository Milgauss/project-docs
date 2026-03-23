"""Live Brave Search snapshot checks — opt-in (real network)."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from api_spend.providers.brave import BraveSnapshotProvider
from api_spend.snapshot_sync import run_snapshot_sync
from api_spend.store import SpendStore

_LIVE = os.environ.get("API_SPEND_LIVE_TESTS", "").strip().lower() in (
    "1",
    "true",
    "yes",
)
_KEY = os.environ.get("API_SPEND_BRAVE_API_KEY", "").strip()

_SKIP = pytest.mark.skipif(
    not (_LIVE and _KEY),
    reason="Set API_SPEND_LIVE_TESTS=1 and API_SPEND_BRAVE_API_KEY",
)


def _dump_snapshot_runs(path: Path, runs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"runs": runs}, indent=2) + "\n", encoding="utf-8")


@_SKIP
def test_live_brave_read_counter():
    with BraveSnapshotProvider(_KEY) as p:
        try:
            n = p.read_counter()
        except Exception as e:
            pytest.fail(f"Brave search probe failed: {e!r}")
        assert isinstance(n, int) and n >= 0


@_SKIP
def test_live_brave_snapshot_sync_twice():
    store = SpendStore.open(":memory:")
    runs: list[dict] = []
    with BraveSnapshotProvider(_KEY) as p:
        t0 = datetime.now(timezone.utc)
        r0 = run_snapshot_sync(store, "brave_search", "requests", p, t0)
        assert r0.error is None, r0.error
        time.sleep(0.05)
        t1 = datetime.now(timezone.utc)
        r1 = run_snapshot_sync(store, "brave_search", "requests", p, t1)
        assert r1.error is None, r1.error
        runs.extend(
            [
                {
                    "recorded_at": t0.isoformat(),
                    "counter_observed": r0.counter_observed,
                    "error": r0.error,
                    "records": [x.model_dump(mode="json") for x in r0.records],
                },
                {
                    "recorded_at": t1.isoformat(),
                    "counter_observed": r1.counter_observed,
                    "error": r1.error,
                    "records": [x.model_dump(mode="json") for x in r1.records],
                },
            ]
        )
        for rec in r1.records:
            assert rec.provider == "brave_search"
            assert rec.service == "requests"

    dump_path = os.environ.get("API_SPEND_LIVE_DUMP_PATH", "").strip()
    if dump_path:
        _dump_snapshot_runs(Path(dump_path).expanduser().resolve(), runs)
