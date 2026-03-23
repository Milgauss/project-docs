"""``run_snapshot_sync`` — delta logic without ``ApiSpend``."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from api_spend.providers.base import SnapshotProvider, utc_quota_period_month
from api_spend.snapshot_sync import run_snapshot_sync
from api_spend.store import SpendStore


class FakeSnapshotProvider(SnapshotProvider):
    def __init__(self, sequence: list[int]) -> None:
        self._sequence = list(sequence)
        self._calls = 0

    def read_counter(self) -> int:
        i = min(self._calls, len(self._sequence) - 1)
        v = self._sequence[i]
        self._calls += 1
        return v

    def estimate_cost(self, usage_delta: int) -> Decimal:
        return Decimal("0.01") * usage_delta

    def validate_credentials(self) -> bool:
        return True


@pytest.fixture
def store() -> SpendStore:
    return SpendStore.open(":memory:")


def test_utc_quota_period_month_naive():
    dt = datetime(2025, 3, 15, 12, 0, 0)
    assert utc_quota_period_month(dt) == "2025-03"


def test_first_sync_snapshot_only_no_spend(store: SpendStore):
    p = FakeSnapshotProvider([100])
    t = datetime(2025, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
    r = run_snapshot_sync(store, "resend", "emails", p, t)
    assert r.error is None
    assert r.counter_observed == 100
    assert r.records == []
    snap = store.get_latest_snapshot("resend")
    assert snap is not None
    assert snap[1] == 100
    assert snap[2] == "2025-06"


def test_second_sync_same_period_emits_spend(store: SpendStore):
    t0 = datetime(2025, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=1)
    p = FakeSnapshotProvider([100, 160])
    run_snapshot_sync(store, "resend", "emails", p, t0)
    r1 = run_snapshot_sync(store, "resend", "emails", p, t1)
    assert r1.error is None
    assert r1.counter_observed == 160
    assert len(r1.records) == 1
    assert r1.records[0].amount == Decimal("0.60")


def test_month_rollover_no_spend_only_snapshot(store: SpendStore):
    store.insert_snapshot(
        "resend",
        datetime(2025, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
        9000,
        "2025-01",
    )
    p = FakeSnapshotProvider([120])
    t = datetime(2025, 2, 3, 12, 0, 0, tzinfo=timezone.utc)
    r = run_snapshot_sync(store, "resend", "emails", p, t)
    assert r.records == []
    assert r.counter_observed == 120


def test_same_utc_day_custom_quota_period_emits_spend(store: SpendStore):
    """Provider can use a day-sized period key (e.g. Resend daily quota)."""

    class Seq(SnapshotProvider):
        def __init__(self) -> None:
            self.n = [5, 12]

        def read_counter(self) -> int:
            return self.n.pop(0)

        def sync_quota_period(self, recorded_at: datetime) -> str:
            return "2025-06-10"

        def estimate_cost(self, usage_delta: int) -> Decimal:
            return Decimal(usage_delta)

        def validate_credentials(self) -> bool:
            return True

    t0 = datetime(2025, 6, 10, 10, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 6, 10, 11, 0, 0, tzinfo=timezone.utc)
    p = Seq()
    run_snapshot_sync(store, "resend", "emails", p, t0)
    r1 = run_snapshot_sync(store, "resend", "emails", p, t1)
    assert r1.error is None
    assert len(r1.records) == 1
    assert r1.records[0].amount == Decimal(7)


def test_read_counter_error_no_snapshot(store: SpendStore):
    class Boom(SnapshotProvider):
        def read_counter(self) -> int:
            raise OSError("network")

        def estimate_cost(self, usage_delta: int) -> Decimal:
            return Decimal(0)

        def validate_credentials(self) -> bool:
            return False

    t = datetime(2025, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
    r = run_snapshot_sync(store, "resend", "emails", Boom(), t)
    assert r.error is not None
    assert store.get_latest_snapshot("resend") is None
