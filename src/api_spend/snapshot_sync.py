"""Snapshot provider sync: counter deltas → estimated ``SpendRecord`` (``PLANNED_INTERFACE.md`` section 3.2)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone

from api_spend.models import SpendRecord
from api_spend.providers.base import SnapshotProvider, utc_quota_period_month
from api_spend.store import SpendStore

logger = logging.getLogger(__name__)

__all__ = ["SnapshotSyncResult", "run_snapshot_sync", "utc_quota_period_month"]


@dataclass(frozen=True)
class SnapshotSyncResult:
    """Outcome of one ``run_snapshot_sync`` call."""

    records: list[SpendRecord]
    error: str | None = None
    counter_observed: int | None = None


def _utc_calendar_date(dt: datetime) -> date:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).date()


def run_snapshot_sync(
    store: SpendStore,
    provider_name: str,
    service: str,
    provider: SnapshotProvider,
    recorded_at: datetime,
) -> SnapshotSyncResult:
    """
    Read usage counter, compare to latest snapshot for the same quota period, optionally
    write one estimated spend row, always append a new snapshot row.
    """
    try:
        current = provider.read_counter()
    except Exception as exc:
        logger.info(
            "snapshot provider=%s read_counter failed: %s",
            provider_name,
            exc,
        )
        return SnapshotSyncResult([], str(exc), None)

    period_now = provider.sync_quota_period(recorded_at)
    meta_before = store.get_sync_metadata(provider_name)
    prev_latest = meta_before[1] if meta_before else None
    prev_row = store.get_latest_snapshot(provider_name)

    if prev_row is None:
        store.insert_snapshot(provider_name, recorded_at, current, period_now)
        store.set_sync_metadata(provider_name, recorded_at, prev_latest)
        return SnapshotSyncResult([], None, current)

    _prev_dt, prev_val, prev_period = prev_row
    if prev_period is None:
        # Legacy rows before ``quota_period``; assume monthly UTC key.
        prev_period = utc_quota_period_month(_prev_dt)

    if period_now != prev_period:
        store.insert_snapshot(provider_name, recorded_at, current, period_now)
        store.set_sync_metadata(provider_name, recorded_at, prev_latest)
        return SnapshotSyncResult([], None, current)

    delta = max(0, current - prev_val)
    spend_day = _utc_calendar_date(recorded_at)
    records: list[SpendRecord] = []
    if delta > 0:
        try:
            amount = provider.estimate_cost(delta)
        except Exception as exc:
            logger.info(
                "snapshot provider=%s estimate_cost failed: %s",
                provider_name,
                exc,
            )
            return SnapshotSyncResult([], str(exc), current)
        records.append(
            SpendRecord(
                provider=provider_name,
                service=service,
                date=spend_day,
                amount=amount,
                currency="USD",
            )
        )
        store.upsert_spend_records(records)
        new_latest = spend_day if prev_latest is None else max(prev_latest, spend_day)
    else:
        new_latest = prev_latest

    store.insert_snapshot(provider_name, recorded_at, current, period_now)
    store.set_sync_metadata(provider_name, recorded_at, new_latest)
    logger.debug(
        "snapshot provider=%s counter=%s records=%d",
        provider_name,
        current,
        len(records),
    )
    return SnapshotSyncResult(records, None, current)
