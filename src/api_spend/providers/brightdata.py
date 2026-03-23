"""Bright Data billing adapter — ``GET /zone/cost`` (``PLANNED_INTERFACE.md`` §3.1)."""

from __future__ import annotations

import calendar
import json
import re
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx

from api_spend.http_raw_dump import BRIGHTDATA_RAW_RESPONSE_ENV, maybe_dump_http_response
from api_spend.models import SpendRecord
from api_spend.providers.base import BillingApiProvider, FetchCostsResult

BRIGHTDATA_API_BASE = "https://api.brightdata.com"
ZONE_COST_PATH = "/zone/cost"
DEFAULT_TIMEOUT = 60.0

_BACK_D = re.compile(r"^back_d(\d+)$")
_BACK_M = re.compile(r"^back_m(\d+)$")


def _rfc3339_range(start: date, end: date) -> tuple[str, str]:
    """Inclusive-style window for Bright Data ``from`` / ``to`` query params."""
    start_s = datetime(start.year, start.month, start.day, tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT00:00:00.000Z"
    )
    end_s = datetime(end.year, end.month, end.day, tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT00:00:00.000Z"
    )
    return start_s, end_s


def _unwrap_zone_periods(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Bright Data returns ``{ "<zone_or_id>": { "back_d0"|"back_m0": { "cost", "bw" }, ... } }``."""
    if not payload:
        return None
    data = payload.get("data")
    if isinstance(data, dict) and data:
        payload = data
    if any(isinstance(v, dict) and "cost" in v for v in payload.values()):
        return payload
    if len(payload) == 1:
        inner = next(iter(payload.values()))
        if isinstance(inner, dict):
            return inner
    return None


def _last_day_of_month(d: date) -> date:
    last = calendar.monthrange(d.year, d.month)[1]
    return date(d.year, d.month, last)


def _month_first_n_months_before(ref: date, n: int) -> date:
    """``back_m0`` = first day of ``ref``'s month; ``back_m1`` = previous month, etc."""
    y, m = ref.year, ref.month
    for _ in range(n):
        if m == 1:
            y -= 1
            m = 12
        else:
            m -= 1
    return date(y, m, 1)


def _month_overlaps_range(m_first: date, start: date, end: date) -> bool:
    """True if some calendar day in ``m_first``'s month lies in ``[start, end)``."""
    m_last = _last_day_of_month(m_first)
    return m_first < end and m_last >= start


def _parse_back_d_records(
    inner: dict[str, Any],
    *,
    zone: str,
    start: date,
    end: date,
    anchor: date,
    provider_name: str,
) -> list[SpendRecord]:
    merged: dict[tuple[date, str], Decimal] = defaultdict(lambda: Decimal("0"))
    z = zone.strip().lower()
    for period_key, raw in inner.items():
        if not isinstance(raw, dict) or "cost" not in raw:
            continue
        m = _BACK_D.match(str(period_key))
        if not m:
            continue
        n = int(m.group(1))
        day = anchor - timedelta(days=n)
        if not (start <= day < end):
            continue
        try:
            amt = Decimal(str(raw["cost"]))
        except Exception:
            continue
        merged[(day, f"{z}:{period_key}")] += amt

    return [
        SpendRecord(
            provider=provider_name,
            service=svc,
            date=day,
            amount=amount,
            currency="USD",
        )
        for (day, svc), amount in sorted(merged.items())
    ]


def _parse_back_m_records(
    inner: dict[str, Any],
    *,
    zone: str,
    start: date,
    end: date,
    ref: date,
    provider_name: str,
) -> list[SpendRecord]:
    """Map ``back_mN`` to the first calendar day of that month (monthly aggregate)."""
    merged: dict[tuple[date, str], Decimal] = defaultdict(lambda: Decimal("0"))
    z = zone.strip().lower()
    for period_key, raw in inner.items():
        if not isinstance(raw, dict) or "cost" not in raw:
            continue
        m = _BACK_M.match(str(period_key))
        if not m:
            continue
        n = int(m.group(1))
        m_first = _month_first_n_months_before(ref, n)
        if not _month_overlaps_range(m_first, start, end):
            continue
        try:
            amt = Decimal(str(raw["cost"]))
        except Exception:
            continue
        merged[(m_first, f"{z}:{period_key}")] += amt

    return [
        SpendRecord(
            provider=provider_name,
            service=svc,
            date=day,
            amount=amount,
            currency="USD",
        )
        for (day, svc), amount in sorted(merged.items())
    ]


def _parse_brightdata_range_date(value: Any) -> date | None:
    """Parse ``DD-MMM-YYYY`` / ``DD-mmm-yyyy`` strings from zone/cost ``range``."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    for fmt in ("%d-%b-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_custom_period(
    inner: dict[str, Any],
    *,
    zone: str,
    start: date,
    end: date,
    provider_name: str,
) -> list[SpendRecord]:
    """Single aggregate from ``{"custom": {"cost", "range": {"from","to"}, ...}}``."""
    raw = inner.get("custom")
    if not isinstance(raw, dict) or "cost" not in raw:
        return []
    try:
        amt = Decimal(str(raw["cost"]))
    except Exception:
        return []

    day = start
    rng = raw.get("range")
    if isinstance(rng, dict):
        parsed = _parse_brightdata_range_date(rng.get("from"))
        if parsed is not None:
            day = parsed
    if day < start or day >= end:
        day = start

    z = zone.strip().lower()
    return [
        SpendRecord(
            provider=provider_name,
            service=f"{z}:custom",
            date=day,
            amount=amt,
            currency="USD",
        )
    ]


def _parse_zone_cost_payload(
    payload: dict[str, Any],
    *,
    zone: str,
    start: date,
    end: date,
    provider_name: str = "brightdata",
) -> list[SpendRecord]:
    """Map ``back_dN`` / ``back_mN`` / ``custom`` payloads to ``SpendRecord``s (§3.1).

    Some zones return a **custom** object (total **cost** for the requested window)
    instead of **back_d** / **back_m** keys. Prefer **daily** rows when any daily
    **cost** is non-zero; else **monthly** when any monthly **cost** is non-zero;
    else **custom** when present; else daily (possibly all zero) or **[]**.
    """
    inner = _unwrap_zone_periods(payload)
    if not inner:
        return []

    ref = end - timedelta(days=1)
    daily = _parse_back_d_records(
        inner, zone=zone, start=start, end=end, anchor=ref, provider_name=provider_name
    )
    monthly = _parse_back_m_records(
        inner, zone=zone, start=start, end=end, ref=ref, provider_name=provider_name
    )
    custom = _parse_custom_period(
        inner, zone=zone, start=start, end=end, provider_name=provider_name
    )

    if any(rec.amount != 0 for rec in daily):
        return daily
    if daily:
        if any(rec.amount != 0 for rec in monthly):
            return monthly
        if any(rec.amount != 0 for rec in custom):
            return custom
        return daily
    if any(rec.amount != 0 for rec in monthly):
        return monthly
    if custom:
        return custom
    return []


class BrightDataBillingProvider(BillingApiProvider):
    """Bright Data zone cost (Bearer token + required ``zone`` query param)."""

    def __init__(
        self,
        *,
        api_key: str,
        zone: str,
        client: httpx.Client | None = None,
        base_url: str = BRIGHTDATA_API_BASE,
    ) -> None:
        self._api_key = api_key.strip()
        self._zone = zone.strip()
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    def _url(self) -> str:
        return f"{self._base_url}{ZONE_COST_PATH}"

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> BrightDataBillingProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_costs(self, start: date, end: date) -> FetchCostsResult:
        if end <= start:
            return FetchCostsResult([], "end must be after start")
        if not self._zone:
            return FetchCostsResult(
                [],
                "brightdata provider requires options.zone in config (zone name)",
            )

        from_s, to_s = _rfc3339_range(start, end)
        try:
            response = self._client.get(
                self._url(),
                params={"zone": self._zone, "from": from_s, "to": to_s},
                headers=self._headers(),
            )
            maybe_dump_http_response(response, BRIGHTDATA_RAW_RESPONSE_ENV)
            if response.status_code != 200:
                return FetchCostsResult(
                    [],
                    _brightdata_http_error("zone/cost", response),
                )
            payload = response.json()
            if not isinstance(payload, dict):
                return FetchCostsResult(
                    [], "Bright Data zone/cost response: expected JSON object"
                )
        except httpx.RequestError as e:
            return FetchCostsResult([], f"Bright Data zone/cost request failed: {e}")

        records = _parse_zone_cost_payload(
            payload, zone=self._zone, start=start, end=end
        )
        return FetchCostsResult(records, None)

    def validate_credentials(self) -> bool:
        if not self._zone:
            return False
        try:
            end = date.today()
            start = end - timedelta(days=1)
            from_s, to_s = _rfc3339_range(start, end)
            r = self._client.get(
                self._url(),
                params={"zone": self._zone, "from": from_s, "to": to_s},
                headers=self._headers(),
            )
            maybe_dump_http_response(r, BRIGHTDATA_RAW_RESPONSE_ENV)
            return r.status_code == 200
        except httpx.RequestError:
            return False


def _brightdata_http_error(context: str, response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            for k in ("message", "error", "detail"):
                v = body.get(k)
                if isinstance(v, str) and v:
                    return f"Bright Data {context} HTTP {response.status_code}: {v}"
    except (json.JSONDecodeError, ValueError):
        pass
    text = response.text or ""
    if len(text) > 200:
        text = text[:200] + "…"
    return f"Bright Data {context} HTTP {response.status_code}: {text or 'no body'}"


def brightdata_options_from_config(options: Mapping[str, Any] | None) -> str:
    if not options:
        return ""
    raw = options.get("zone")
    return str(raw).strip() if raw is not None else ""
