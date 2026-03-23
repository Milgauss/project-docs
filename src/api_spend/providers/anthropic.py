"""Anthropic billing adapter — Admin API ``GET /v1/organizations/cost_report`` (§3.1)."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx

from api_spend.http_raw_dump import ANTHROPIC_RAW_RESPONSE_ENV, maybe_dump_http_response
from api_spend.models import SpendRecord
from api_spend.providers.base import BillingApiProvider, FetchCostsResult

ANTHROPIC_API_BASE = "https://api.anthropic.com"
COST_REPORT_PATH = "/v1/organizations/cost_report"
DEFAULT_TIMEOUT = 60.0

# Admin keys used for cost report (``PLANNED_INTERFACE.md`` §3.1).
_ADMIN_KEY_PREFIX = "sk-ant-admin"

# Anthropic expects repeated ``group_by[]`` query keys, not a single ``group_by`` array.
_COST_REPORT_GROUP_BY = ("workspace_id", "description")


def _cost_report_params(
    *,
    starting_at: str,
    ending_at: str,
    bucket_width: str,
    limit: int,
    page: str | None,
) -> list[tuple[str, str | int]]:
    q: list[tuple[str, str | int]] = [
        ("starting_at", starting_at),
        ("ending_at", ending_at),
        ("bucket_width", bucket_width),
        ("limit", limit),
    ]
    for g in _COST_REPORT_GROUP_BY:
        q.append(("group_by[]", g))
    if page is not None:
        q.append(("page", page))
    return q


def _rfc3339_utc_midnight(d: date) -> str:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).strftime(
        "%Y-%m-%dT00:00:00Z"
    )


def _parse_bucket_start_date(starting_at: str) -> date | None:
    try:
        if len(starting_at) >= 10:
            return date.fromisoformat(starting_at[:10])
    except ValueError:
        pass
    return None


def _anthropic_service(row: dict[str, Any]) -> str:
    parts: list[str] = []
    ws = row.get("workspace_id")
    if ws is not None and str(ws).strip():
        parts.append(str(ws).strip().lower())
    model = row.get("model")
    if model is not None and str(model).strip():
        parts.append(str(model).strip().lower())
    ct = row.get("cost_type")
    if ct is not None and str(ct).strip():
        parts.append(str(ct).strip().lower())
    tt = row.get("token_type")
    if tt is not None and str(tt).strip():
        parts.append(str(tt).strip().lower())
    if parts:
        return ":".join(parts)
    desc = row.get("description")
    if desc is not None and str(desc).strip():
        return str(desc).strip().lower()
    return "unattributed"


def _amount_usd_minor_string(amount_raw: Any) -> Decimal | None:
    """Convert API ``amount`` (minor units, e.g. cents) to USD ``Decimal``."""
    if amount_raw is None:
        return None
    try:
        minor = Decimal(str(amount_raw))
    except Exception:
        return None
    return minor / Decimal(100)


def _parse_cost_report_buckets(
    buckets: list[dict[str, Any]],
    *,
    provider_name: str = "anthropic",
) -> list[SpendRecord]:
    merged: dict[tuple[date, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for bucket in buckets:
        day = _parse_bucket_start_date(str(bucket.get("starting_at") or ""))
        if day is None:
            continue
        for row in bucket.get("results") or []:
            if not isinstance(row, dict):
                continue
            amt = _amount_usd_minor_string(row.get("amount"))
            if amt is None:
                continue
            currency = (row.get("currency") or "USD").upper()
            if currency != "USD":
                continue
            svc = _anthropic_service(row)
            merged[(day, svc)] += amt

    out: list[SpendRecord] = []
    for (day, svc), amount in sorted(merged.items()):
        out.append(
            SpendRecord(
                provider=provider_name,
                service=svc,
                date=day,
                amount=amount,
                currency="USD",
            )
        )
    return out


class AnthropicBillingProvider(BillingApiProvider):
    """Anthropic organization cost report (admin API key)."""

    def __init__(
        self,
        *,
        api_key: str,
        client: httpx.Client | None = None,
        base_url: str = ANTHROPIC_API_BASE,
    ) -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
        }

    def _url(self) -> str:
        return f"{self._base_url}{COST_REPORT_PATH}"

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> AnthropicBillingProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_costs(self, start: date, end: date) -> FetchCostsResult:
        if end <= start:
            return FetchCostsResult([], "end must be after start")
        if not self._api_key.startswith(_ADMIN_KEY_PREFIX):
            return FetchCostsResult(
                [],
                "anthropic cost report requires an admin API key (sk-ant-admin…)",
            )

        starting_at = _rfc3339_utc_midnight(start)
        ending_at = _rfc3339_utc_midnight(end)

        all_buckets: list[dict[str, Any]] = []
        page: str | None = None
        try:
            while True:
                params = _cost_report_params(
                    starting_at=starting_at,
                    ending_at=ending_at,
                    bucket_width="1d",
                    limit=31,
                    page=page,
                )
                response = self._client.get(
                    self._url(),
                    params=params,
                    headers=self._headers(),
                )
                maybe_dump_http_response(response, ANTHROPIC_RAW_RESPONSE_ENV)
                if response.status_code != 200:
                    return FetchCostsResult(
                        [],
                        _anthropic_http_error("cost_report", response),
                    )
                payload = response.json()
                if not isinstance(payload, dict):
                    return FetchCostsResult(
                        [], "Anthropic cost_report response: expected JSON object"
                    )
                data = payload.get("data")
                if not isinstance(data, list):
                    return FetchCostsResult(
                        [], "Anthropic cost_report response: missing data array"
                    )
                for item in data:
                    if isinstance(item, dict):
                        all_buckets.append(item)
                if not payload.get("has_more"):
                    break
                page = payload.get("next_page")
                if not page:
                    break
        except httpx.RequestError as e:
            return FetchCostsResult([], f"Anthropic cost_report request failed: {e}")

        records = _parse_cost_report_buckets(all_buckets)
        return FetchCostsResult(records, None)

    def validate_credentials(self) -> bool:
        if not self._api_key.startswith(_ADMIN_KEY_PREFIX):
            return False
        try:
            end = date.today()
            start = end - timedelta(days=1)
            params = _cost_report_params(
                starting_at=_rfc3339_utc_midnight(start),
                ending_at=_rfc3339_utc_midnight(end),
                bucket_width="1d",
                limit=1,
                page=None,
            )
            r = self._client.get(
                self._url(),
                params=params,
                headers=self._headers(),
            )
            maybe_dump_http_response(r, ANTHROPIC_RAW_RESPONSE_ENV)
            return r.status_code == 200
        except httpx.RequestError:
            return False


def _anthropic_http_error(context: str, response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            err = body.get("error")
            if isinstance(err, dict):
                msg = err.get("message")
                if msg:
                    return f"Anthropic {context} HTTP {response.status_code}: {msg}"
            if isinstance(err, str):
                return f"Anthropic {context} HTTP {response.status_code}: {err}"
    except (json.JSONDecodeError, ValueError):
        pass
    text = response.text or ""
    if len(text) > 200:
        text = text[:200] + "…"
    return f"Anthropic {context} HTTP {response.status_code}: {text or 'no body'}"
