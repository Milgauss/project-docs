"""SQLite store: schema, CRUD, reset, size."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest

from api_spend.exceptions import StoreError
from api_spend.models import SpendRecord
from api_spend.store import DB_FILENAME, SpendStore, default_database_path


@pytest.fixture
def store():
    s = SpendStore.open(":memory:")
    yield s
    s.close()


def _record(**kwargs):
    defaults = dict(
        provider="openai",
        service="gpt-4o",
        date=date(2025, 1, 15),
        amount=Decimal("1.25"),
        currency="USD",
    )
    defaults.update(kwargs)
    return SpendRecord(**defaults)


def test_insert_and_query_decimal_roundtrip(store):
    store.upsert_spend_records([_record()])
    rows = store.query_spend_records(date(2025, 1, 1), date(2025, 2, 1))
    assert len(rows) == 1
    assert rows[0].amount == Decimal("1.25")
    assert rows[0].provider == "openai"


def test_upsert_replaces_same_provider_service_date(store):
    store.upsert_spend_records([_record(amount=Decimal("1.00"))])
    store.upsert_spend_records([_record(amount=Decimal("2.50"))])
    rows = store.query_spend_records(date(2025, 1, 1), date(2025, 2, 1))
    assert len(rows) == 1
    assert rows[0].amount == Decimal("2.50")


def test_date_range_inclusive_start_exclusive_end(store):
    store.upsert_spend_records(
        [
            _record(date=date(2025, 1, 1)),
            _record(date=date(2025, 1, 31)),
            _record(date=date(2025, 2, 1)),
        ]
    )
    rows = store.query_spend_records(date(2025, 1, 1), date(2025, 2, 1))
    dates = {r.date for r in rows}
    assert dates == {date(2025, 1, 1), date(2025, 1, 31)}
    assert date(2025, 2, 1) not in dates


def test_provider_filter(store):
    store.upsert_spend_records(
        [
            _record(provider="openai"),
            _record(provider="anthropic", service="claude", date=date(2025, 1, 16)),
        ]
    )
    rows = store.query_spend_records(
        date(2025, 1, 1),
        date(2025, 2, 1),
        providers=["openai"],
    )
    assert len(rows) == 1
    assert rows[0].provider == "openai"


def test_sync_metadata_roundtrip(store):
    ts = datetime(2025, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
    ld = date(2025, 1, 19)
    store.set_sync_metadata("openai", ts, ld)
    got = store.get_sync_metadata("openai")
    assert got is not None
    last_synced, latest_date = got
    assert last_synced.replace(microsecond=0) == ts.replace(microsecond=0)
    assert latest_date == ld


def test_get_sync_metadata_missing(store):
    assert store.get_sync_metadata("openai") is None


def test_snapshot_latest_is_most_recent(store):
    base = datetime(2025, 1, 1, tzinfo=timezone.utc)
    store.insert_snapshot("resend", base, 100)
    store.insert_snapshot("resend", base + timedelta(hours=1), 150)
    got = store.get_latest_snapshot("resend")
    assert got is not None
    recorded_at, counter, period = got
    assert counter == 150
    assert period is None
    assert recorded_at == base + timedelta(hours=1)


def test_get_latest_snapshot_missing(store):
    assert store.get_latest_snapshot("resend") is None


def test_insert_snapshot_stores_quota_period(store):
    dt = datetime(2025, 4, 1, tzinfo=timezone.utc)
    store.insert_snapshot("resend", dt, 7, "2025-04")
    got = store.get_latest_snapshot("resend")
    assert got is not None
    assert got[2] == "2025-04"


def test_reset_all(store):
    store.upsert_spend_records([_record()])
    store.set_sync_metadata("openai", datetime.now(timezone.utc), date(2025, 1, 1))
    store.insert_snapshot("resend", datetime.now(timezone.utc), 1)
    store.reset()
    assert store.query_spend_records(date(2000, 1, 1), date(2030, 1, 1)) == []
    assert store.get_sync_metadata("openai") is None
    assert store.get_latest_snapshot("resend") is None


def test_reset_single_provider(store):
    store.upsert_spend_records([_record(provider="openai"), _record(provider="anthropic", service="x")])
    store.set_sync_metadata("openai", datetime.now(timezone.utc), date(2025, 1, 1))
    store.set_sync_metadata("anthropic", datetime.now(timezone.utc), date(2025, 1, 1))
    store.insert_snapshot("openai", datetime.now(timezone.utc), 1)
    store.insert_snapshot("anthropic", datetime.now(timezone.utc), 2)
    store.reset(providers=["openai"])
    assert len(store.query_spend_records(date(2000, 1, 1), date(2030, 1, 1))) == 1
    assert store.query_spend_records(date(2000, 1, 1), date(2030, 1, 1))[0].provider == "anthropic"
    assert store.get_sync_metadata("openai") is None
    assert store.get_sync_metadata("anthropic") is not None
    assert store.get_latest_snapshot("openai") is None
    assert store.get_latest_snapshot("anthropic") is not None


def test_approximate_size_bytes_positive(store):
    store.upsert_spend_records([_record()])
    assert store.approximate_size_bytes() > 0


def test_default_database_path_ends_with_filename():
    p = default_database_path()
    assert p.name == DB_FILENAME


def test_open_creates_parent_dirs(tmp_path):
    db = tmp_path / "nested" / "deep" / DB_FILENAME
    store = SpendStore.open(db)
    try:
        assert db.is_file()
        store.upsert_spend_records([_record()])
    finally:
        store.close()


def test_open_file_as_directory_raises_store_error(tmp_path):
    d = tmp_path / "not_a_file"
    d.mkdir()
    with pytest.raises(StoreError, match="cannot open store"):
        SpendStore.open(d)
