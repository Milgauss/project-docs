"""Query engine: buckets, grouping, coverage, gaps."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from api_spend.models import SpendRecord
from api_spend.query import iter_bucket_periods, run_query
from api_spend.store import SpendStore


@pytest.fixture
def store():
    s = SpendStore.open(":memory:")
    yield s
    s.close()


def _cfg(*names: str) -> list[str]:
    return list(names)


def test_daily_seven_contiguous_days(store):
    start, end = date(2025, 1, 1), date(2025, 1, 8)
    for i in range(7):
        store.upsert_spend_records(
            [
                SpendRecord(
                    provider="openai",
                    service="gpt-4o",
                    date=start + timedelta(days=i),
                    amount=Decimal("1"),
                    currency="USD",
                )
            ]
        )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai"),
        group_by=None,
    )
    assert len(r.buckets) == 7
    assert sum(b.amount for b in r.buckets) == Decimal("7")
    assert all(b.coverage == "complete" for b in r.buckets)
    assert r.gaps == []


def test_weekly_two_buckets_fourteen_days(store):
    # Monday 2025-06-02 .. Monday 2025-06-16 (14 days)
    start, end = date(2025, 6, 2), date(2025, 6, 16)
    d = start
    while d < end:
        store.upsert_spend_records(
            [
                SpendRecord(
                    provider="openai",
                    service="x",
                    date=d,
                    amount=Decimal("10"),
                    currency="USD",
                )
            ]
        )
        d += timedelta(days=1)
    r = run_query(
        store,
        start,
        end,
        granularity="week",
        configured_providers=_cfg("openai"),
    )
    assert len(r.buckets) == 2
    assert r.buckets[0].period_start == date(2025, 6, 2)
    assert r.buckets[0].period_end == date(2025, 6, 9)
    assert r.buckets[1].period_start == date(2025, 6, 9)
    assert r.buckets[1].period_end == date(2025, 6, 16)
    assert r.buckets[0].amount == Decimal("70")
    assert r.buckets[1].amount == Decimal("70")


def test_monthly_three_months(store):
    start, end = date(2025, 1, 1), date(2025, 4, 1)
    for m in range(1, 4):
        for day in range(1, 29):  # simplify: 28 days per month in Q1 for fixture
            store.upsert_spend_records(
                [
                    SpendRecord(
                        provider="openai",
                        service="x",
                        date=date(2025, m, day),
                        amount=Decimal("1"),
                        currency="USD",
                    )
                ]
            )
    r = run_query(
        store,
        start,
        end,
        granularity="month",
        configured_providers=_cfg("openai"),
    )
    assert len(r.buckets) == 3
    assert r.buckets[0].amount == Decimal("28")
    assert r.buckets[1].amount == Decimal("28")
    assert r.buckets[2].amount == Decimal("28")


def test_group_by_provider(store):
    start, end = date(2025, 1, 1), date(2025, 1, 4)
    store.upsert_spend_records(
        [
            SpendRecord(
                provider="openai",
                service="a",
                date=date(2025, 1, 1),
                amount=Decimal("1"),
                currency="USD",
            ),
            SpendRecord(
                provider="anthropic",
                service="b",
                date=date(2025, 1, 1),
                amount=Decimal("2"),
                currency="USD",
            ),
        ]
    )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai", "anthropic"),
        group_by="provider",
    )
    assert len(r.buckets) == 6  # 3 days * 2 providers
    by_p = {}
    for b in r.buckets:
        if b.period_start == date(2025, 1, 1):
            by_p[b.group["provider"]] = b.amount
    assert by_p["openai"] == Decimal("1")
    assert by_p["anthropic"] == Decimal("2")


def test_group_by_service(store):
    start, end = date(2025, 1, 1), date(2025, 1, 3)
    store.upsert_spend_records(
        [
            SpendRecord(
                provider="openai",
                service="s1",
                date=date(2025, 1, 1),
                amount=Decimal("5"),
                currency="USD",
            ),
            SpendRecord(
                provider="openai",
                service="s2",
                date=date(2025, 1, 1),
                amount=Decimal("3"),
                currency="USD",
            ),
        ]
    )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai"),
        group_by="service",
    )
    day1 = [b for b in r.buckets if b.period_start == date(2025, 1, 1)]
    am = {b.group["service"]: b.amount for b in day1}
    assert am["s1"] == Decimal("5")
    assert am["s2"] == Decimal("3")


def test_group_by_provider_and_service(store):
    start, end = date(2025, 1, 1), date(2025, 1, 2)
    store.upsert_spend_records(
        [
            SpendRecord(
                provider="openai",
                service="m1",
                date=date(2025, 1, 1),
                amount=Decimal("1"),
                currency="USD",
            ),
            SpendRecord(
                provider="openai",
                service="m2",
                date=date(2025, 1, 1),
                amount=Decimal("2"),
                currency="USD",
            ),
        ]
    )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai"),
        group_by=["provider", "service"],
    )
    day1 = [b for b in r.buckets if b.period_start == date(2025, 1, 1)]
    keys = {(b.group["provider"], b.group["service"]) for b in day1}
    assert keys == {("openai", "m1"), ("openai", "m2")}


def test_group_by_none_single_total_per_bucket(store):
    start, end = date(2025, 1, 1), date(2025, 1, 2)
    store.upsert_spend_records(
        [
            SpendRecord(
                provider="openai",
                service="a",
                date=date(2025, 1, 1),
                amount=Decimal("1"),
                currency="USD",
            ),
            SpendRecord(
                provider="openai",
                service="b",
                date=date(2025, 1, 1),
                amount=Decimal("2"),
                currency="USD",
            ),
        ]
    )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai"),
        group_by=None,
    )
    day1 = next(b for b in r.buckets if b.period_start == date(2025, 1, 1))
    assert day1.group is None
    assert day1.amount == Decimal("3")


def test_missing_data_partial_and_gap(store):
    start, end = date(2025, 1, 1), date(2025, 1, 8)
    for i in (0, 1, 2):
        store.upsert_spend_records(
            [
                SpendRecord(
                    provider="openai",
                    service="x",
                    date=start + timedelta(days=i),
                    amount=Decimal("1"),
                    currency="USD",
                )
            ]
        )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai"),
    )
    partial = [b for b in r.buckets if b.coverage == "partial"]
    assert len(partial) == 4
    assert len(r.gaps) == 1
    assert r.gaps[0].provider == "openai"
    assert r.gaps[0].start == date(2025, 1, 4)
    assert r.gaps[0].end == date(2025, 1, 8)


def test_estimated_only_snapshot_provider(store):
    start, end = date(2025, 1, 1), date(2025, 1, 3)
    store.upsert_spend_records(
        [
            SpendRecord(
                provider="resend",
                service="email",
                date=date(2025, 1, 1),
                amount=Decimal("0.04"),
                currency="USD",
            ),
        ]
    )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("resend"),
    )
    day1 = next(b for b in r.buckets if b.period_start == date(2025, 1, 1))
    assert day1.coverage == "estimated"


def test_empty_store_zero_partial_gaps(store):
    start, end = date(2025, 1, 1), date(2025, 1, 8)
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai", "anthropic"),
    )
    assert len(r.buckets) == 7
    assert all(b.amount == 0 for b in r.buckets)
    assert all(b.coverage == "partial" for b in r.buckets)
    assert len(r.gaps) == 2
    assert {g.provider for g in r.gaps} == {"openai", "anthropic"}


def test_provider_filter_buckets_and_gaps(store):
    start, end = date(2025, 1, 1), date(2025, 1, 4)
    for i in range(3):
        store.upsert_spend_records(
            [
                SpendRecord(
                    provider="openai",
                    service="x",
                    date=start + timedelta(days=i),
                    amount=Decimal("5"),
                    currency="USD",
                ),
            ]
        )
    r = run_query(
        store,
        start,
        end,
        granularity="day",
        configured_providers=_cfg("openai", "anthropic"),
        providers=["openai"],
    )
    assert r.providers_included == ["openai"]
    assert r.gaps == []
    day1 = next(b for b in r.buckets if b.period_start == date(2025, 1, 1))
    assert day1.amount == Decimal("5")


def test_iter_bucket_periods_week_partial_first_segment():
    start, end = date(2025, 6, 4), date(2025, 6, 16)  # Wed .. Mon (12 days)
    periods = list(iter_bucket_periods(start, end, "week"))
    assert periods[0] == (date(2025, 6, 4), date(2025, 6, 9))  # Wed -> Mon
    assert periods[1] == (date(2025, 6, 9), date(2025, 6, 16))


def test_invalid_provider_filter_raises(store):
    with pytest.raises(ValueError, match="not in configured"):
        run_query(
            store,
            date(2025, 1, 1),
            date(2025, 1, 2),
            configured_providers=_cfg("openai"),
            providers=["anthropic"],
        )
