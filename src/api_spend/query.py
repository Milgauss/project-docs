"""
Time-range spend query engine (``PLANNED_INTERFACE.md`` §5.2).

**Bucket boundaries (v1):**

- **day** — each calendar day in ``[start, end)``.
- **week** — segments along **ISO weekday** (Monday = 0). The first segment begins at
  ``start`` (may be shorter than 7 days); each subsequent segment runs until the next Monday
  or ``end``, whichever comes first.
- **month** — **calendar months**: each segment runs from ``cursor`` to the earlier of
  ``end`` and the first day of the following month.

``configured_providers`` lists all providers from config; ``providers`` optionally restricts
the query. Gap detection and ``providers_included`` use that scope. ``snapshot_providers``
defaults to ``SNAPSHOT_PROVIDERS`` from ``config`` (Resend, Brave Search).
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from api_spend.config import SNAPSHOT_PROVIDERS
from api_spend.models import GapInfo, QueryResult, SpendBucket, SpendRecord
from api_spend.store import SpendStore

V1_QUERY_CURRENCY = "USD"

_GAP_REASON = "no spend data for this date range"


def _daterange(a: date, b: date) -> Iterator[date]:
    d = a
    while d < b:
        yield d
        d += timedelta(days=1)


def _first_of_next_month(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def iter_bucket_periods(
    start: date,
    end: date,
    granularity: Literal["day", "week", "month"],
) -> Iterator[tuple[date, date]]:
    cur = start
    while cur < end:
        if granularity == "day":
            nxt = min(end, cur + timedelta(days=1))
        elif granularity == "week":
            if cur.weekday() == 0:
                delta = 7
            else:
                delta = 7 - cur.weekday()
            nxt = min(end, cur + timedelta(days=delta))
        else:
            nxt = min(end, _first_of_next_month(cur))
        yield cur, nxt
        cur = nxt


def _normalize_group_by(group_by: str | list[str] | None) -> tuple[str, ...] | None:
    if group_by is None:
        return None
    if isinstance(group_by, str):
        keys = (group_by,)
    else:
        keys = tuple(group_by)
    allowed = {"provider", "service"}
    bad = set(keys) - allowed
    if bad:
        raise ValueError(f"group_by keys must be subset of {allowed!r}, got {bad!r}")
    if len(set(keys)) != len(keys):
        raise ValueError("group_by list must not duplicate keys")
    return tuple(sorted(keys))


def _day_has_record_for_provider(
    by_dps: dict[tuple[date, str, str], Decimal],
    d: date,
    provider: str,
) -> bool:
    return any(k[0] == d and k[1] == provider for k in by_dps)


def _day_has_record_for_pair(
    by_dps: dict[tuple[date, str, str], Decimal],
    d: date,
    provider: str,
    service: str,
) -> bool:
    return (d, provider, service) in by_dps


def _bucket_amount(
    by_dps: dict[tuple[date, str, str], Decimal],
    bs: date,
    be: date,
    target_providers: frozenset[str],
    group: dict[str, str] | None,
) -> Decimal:
    total = Decimal(0)
    for d in _daterange(bs, be):
        for (rd, rp, rs), amt in by_dps.items():
            if rd != d or rp not in target_providers:
                continue
            if group is None:
                total += amt
            elif group.keys() == {"provider"}:
                if rp == group["provider"]:
                    total += amt
            elif group.keys() == {"service"}:
                if rs == group["service"]:
                    total += amt
            else:
                if rp == group["provider"] and rs == group["service"]:
                    total += amt
    return total


def _snapshot_amount_in_bucket(
    by_dps: dict[tuple[date, str, str], Decimal],
    bs: date,
    be: date,
    target_providers: frozenset[str],
    snapshot_providers: frozenset[str],
    group: dict[str, str] | None,
) -> Decimal:
    total = Decimal(0)
    for d in _daterange(bs, be):
        for (rd, rp, rs), amt in by_dps.items():
            if rd != d or rp not in target_providers or rp not in snapshot_providers:
                continue
            if group is None:
                total += amt
            elif group.keys() == {"provider"}:
                if rp == group["provider"]:
                    total += amt
            elif group.keys() == {"service"}:
                if rs == group["service"]:
                    total += amt
            else:
                if rp == group["provider"] and rs == group["service"]:
                    total += amt
    return total


def _coverage_for_bucket(
    by_dps: dict[tuple[date, str, str], Decimal],
    bs: date,
    be: date,
    qstart: date,
    qend: date,
    target_providers: frozenset[str],
    snapshot_providers: frozenset[str],
    group: dict[str, str] | None,
    total: Decimal,
    snap_total: Decimal,
) -> Literal["complete", "partial", "estimated"]:
    days = list(_daterange(bs, be))

    if group is None:
        if total == 0:
            return "partial"
        if snap_total > 0:
            return "estimated"
        for p in target_providers:
            if p in snapshot_providers:
                continue
            for d in days:
                if not _day_has_record_for_provider(by_dps, d, p):
                    return "partial"
        return "complete"

    if group.keys() == {"provider"}:
        p = group["provider"]
        if p in snapshot_providers:
            return "estimated" if total > 0 else "partial"
        for d in days:
            if not _day_has_record_for_provider(by_dps, d, p):
                return "partial"
        return "complete"

    if group.keys() == {"service"}:
        s = group["service"]
        if snap_total > 0:
            return "estimated"
        billings = [
            p
            for p in target_providers
            if p not in snapshot_providers
            and any(
                k[1] == p and k[2] == s and qstart <= k[0] < qend for k in by_dps
            )
        ]
        if not billings:
            return "partial" if total == 0 else "estimated"
        for p in billings:
            for d in days:
                if not _day_has_record_for_pair(by_dps, d, p, s):
                    return "partial"
        return "complete"

    # provider + service
    p, s = group["provider"], group["service"]
    if p in snapshot_providers:
        return "estimated" if total > 0 else "partial"
    for d in days:
        if not _day_has_record_for_pair(by_dps, d, p, s):
            return "partial"
    return "complete"


def _build_gaps(
    by_dps: dict[tuple[date, str, str], Decimal],
    start: date,
    end: date,
    target_providers: Sequence[str],
) -> list[GapInfo]:
    gaps: list[GapInfo] = []
    for p in target_providers:
        missing: list[date] = []
        for d in _daterange(start, end):
            if not _day_has_record_for_provider(by_dps, d, p):
                missing.append(d)
        if not missing:
            continue
        missing.sort()
        rs = missing[0]
        prev = missing[0]
        for d in missing[1:]:
            if d == prev + timedelta(days=1):
                prev = d
            else:
                gaps.append(
                    GapInfo(
                        provider=p,
                        start=rs,
                        end=prev + timedelta(days=1),
                        reason=_GAP_REASON,
                    )
                )
                rs = d
                prev = d
        gaps.append(
            GapInfo(
                provider=p,
                start=rs,
                end=prev + timedelta(days=1),
                reason=_GAP_REASON,
            )
        )
    return gaps


def _iter_group_dicts(
    gb: tuple[str, ...] | None,
    target_providers: tuple[str, ...],
    by_dps: dict[tuple[date, str, str], Decimal],
    start: date,
    end: date,
) -> list[dict[str, str] | None]:
    if gb is None:
        return [None]
    if gb == ("provider",):
        return [{"provider": p} for p in target_providers]
    if gb == ("service",):
        services: set[str] = set()
        for (d, p, s), _ in by_dps.items():
            if p in target_providers and start <= d < end:
                services.add(s)
        return [{"service": s} for s in sorted(services)]
    # provider + service
    pairs: set[tuple[str, str]] = set()
    for (d, p, s), _ in by_dps.items():
        if p in target_providers and start <= d < end:
            pairs.add((p, s))
    out = [{"provider": p, "service": s} for p, s in sorted(pairs)]
    return out


def _group_sort_key(g: dict[str, str] | None) -> tuple:
    if g is None:
        return ()
    return tuple(sorted(g.items()))


def run_query(
    store: SpendStore,
    start: date,
    end: date,
    *,
    granularity: Literal["day", "week", "month"] = "day",
    configured_providers: Sequence[str],
    providers: list[str] | None = None,
    group_by: str | list[str] | None = None,
    snapshot_providers: frozenset[str] | None = None,
) -> QueryResult:
    """
    Build a ``QueryResult`` from the local store.

    ``configured_providers`` must list every provider from YAML (used for gaps and for
    interpreting ``providers=None``). ``providers``, when set, must be a subset.
    """
    if end <= start:
        raise ValueError("end must be after start")

    cfg_set = frozenset(configured_providers)
    if not cfg_set:
        raise ValueError("configured_providers must be non-empty")

    if providers is None:
        target = tuple(sorted(cfg_set))
    else:
        for p in providers:
            if p not in cfg_set:
                raise ValueError(
                    f"provider {p!r} is not in configured_providers"
                )
        target = tuple(sorted(providers))

    target_f = frozenset(target)
    snaps = snapshot_providers if snapshot_providers is not None else SNAPSHOT_PROVIDERS

    gb = _normalize_group_by(group_by)
    recs: list[SpendRecord] = store.query_spend_records(start, end, list(target))
    by_dps: dict[tuple[date, str, str], Decimal] = {}
    for r in recs:
        k = (r.date, r.provider, r.service)
        by_dps[k] = by_dps.get(k, Decimal(0)) + r.amount

    gaps = _build_gaps(by_dps, start, end, target)
    group_dicts = _iter_group_dicts(gb, target, by_dps, start, end)

    buckets: list[SpendBucket] = []
    for bs, be in iter_bucket_periods(start, end, granularity):
        for g in group_dicts:
            total = _bucket_amount(by_dps, bs, be, target_f, g)
            snap_total = _snapshot_amount_in_bucket(
                by_dps, bs, be, target_f, snaps, g
            )
            cov = _coverage_for_bucket(
                by_dps,
                bs,
                be,
                start,
                end,
                target_f,
                snaps,
                g,
                total,
                snap_total,
            )
            buckets.append(
                SpendBucket(
                    period_start=bs,
                    period_end=be,
                    group=g,
                    amount=total,
                    currency=V1_QUERY_CURRENCY,
                    coverage=cov,
                )
            )

    buckets.sort(key=lambda b: (b.period_start, b.period_end, _group_sort_key(b.group)))

    return QueryResult(
        buckets=buckets,
        providers_included=list(target),
        gaps=gaps,
    )
