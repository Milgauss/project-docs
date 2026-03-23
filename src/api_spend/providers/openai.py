"""OpenAI billing adapter — ``GET /v1/organization/costs`` (``PLANNED_INTERFACE.md`` §3.1)."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from api_spend.http_raw_dump import OPENAI_RAW_RESPONSE_ENV, maybe_dump_http_response
from api_spend.models import SpendRecord
from api_spend.providers.base import BillingApiProvider, FetchCostsResult

OPENAI_API_BASE = "https://api.openai.com/v1"
COSTS_PATH = "/organization/costs"
DEFAULT_TIMEOUT = 60.0


def _date_start_unix_utc(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def _service_from_result(project_id: Any, line_item: Any) -> str:
    """Map API row to ``SpendRecord.service`` (model/line_item; ``project_id:…`` when set)."""
    raw_item = line_item if line_item is not None else None
    base = (str(raw_item).strip().lower() if raw_item else "") or "unattributed"
    pid = project_id if project_id is not None else None
    if pid:
        return f"{str(pid).strip().lower()}:{base}"
    return base


def _parse_costs_buckets(
    buckets: list[dict[str, Any]],
    *,
    provider_name: str = "openai",
) -> list[SpendRecord]:
    """Turn API ``data`` buckets into spend records (merge same day+service)."""
    merged: dict[tuple[date, str], Decimal] = defaultdict(lambda: Decimal("0"))
    for bucket in buckets:
        start_ts = bucket.get("start_time")
        if start_ts is None:
            continue
        day = datetime.fromtimestamp(int(start_ts), tz=timezone.utc).date()
        for row in bucket.get("results") or []:
            if not isinstance(row, dict):
                continue
            amt = row.get("amount") or {}
            value = amt.get("value")
            if value is None:
                continue
            currency = (amt.get("currency") or "usd").upper()
            service = _service_from_result(row.get("project_id"), row.get("line_item"))
            key = (day, service)
            merged[key] += Decimal(str(value))

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


class OpenAIBillingProvider(BillingApiProvider):
    """OpenAI organization costs API (admin key + ``OpenAI-Organization`` header)."""

    def __init__(
        self,
        *,
        api_key: str,
        organization_id: str,
        client: httpx.Client | None = None,
        base_url: str = OPENAI_API_BASE,
    ) -> None:
        self._api_key = api_key
        self._organization_id = organization_id.strip()
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "OpenAI-Organization": self._organization_id,
        }

    def _costs_url(self) -> str:
        return f"{self._base_url}{COSTS_PATH}"

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenAIBillingProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_costs(self, start: date, end: date) -> FetchCostsResult:
        if end <= start:
            return FetchCostsResult([], "end must be after start")
        if not self._organization_id:
            return FetchCostsResult(
                [],
                "openai provider requires options.organization_id in config",
            )

        start_ts = _date_start_unix_utc(start)
        end_ts = _date_start_unix_utc(end)

        all_buckets: list[dict[str, Any]] = []
        page: str | None = None
        try:
            while True:
                params: dict[str, Any] = {
                    "start_time": start_ts,
                    "end_time": end_ts,
                    "bucket_width": "1d",
                    "limit": 180,
                    "group_by": ["project_id", "line_item"],
                }
                if page is not None:
                    params["page"] = page
                response = self._client.get(
                    self._costs_url(),
                    params=params,
                    headers=self._headers(),
                )
                maybe_dump_http_response(response, OPENAI_RAW_RESPONSE_ENV)
                if response.status_code != 200:
                    return FetchCostsResult(
                        [],
                        _http_error_message("costs", response),
                    )
                payload = response.json()
                if not isinstance(payload, dict):
                    return FetchCostsResult([], "OpenAI costs response: expected JSON object")
                data = payload.get("data")
                if not isinstance(data, list):
                    return FetchCostsResult([], "OpenAI costs response: missing data array")
                for item in data:
                    if isinstance(item, dict):
                        all_buckets.append(item)
                page = payload.get("next_page")
                if not page:
                    break
        except httpx.RequestError as e:
            return FetchCostsResult([], f"OpenAI costs request failed: {e}")

        records = _parse_costs_buckets(all_buckets)
        return FetchCostsResult(records, None)

    def validate_credentials(self) -> bool:
        if not self._organization_id:
            return False
        try:
            now = int(datetime.now(tz=timezone.utc).timestamp())
            params = {
                "start_time": now - 86400,
                "end_time": now,
                "bucket_width": "1d",
                "limit": 1,
                "group_by": ["line_item"],
            }
            r = self._client.get(
                self._costs_url(),
                params=params,
                headers=self._headers(),
            )
            maybe_dump_http_response(r, OPENAI_RAW_RESPONSE_ENV)
            return r.status_code == 200
        except httpx.RequestError:
            return False


def _http_error_message(context: str, response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            err = body.get("error")
            if isinstance(err, dict) and err.get("message"):
                return f"OpenAI {context} HTTP {response.status_code}: {err['message']}"
            if isinstance(err, str):
                return f"OpenAI {context} HTTP {response.status_code}: {err}"
    except (json.JSONDecodeError, ValueError):
        pass
    text = response.text or ""
    if len(text) > 200:
        text = text[:200] + "…"
    return f"OpenAI {context} HTTP {response.status_code}: {text or 'no body'}"


def openai_options_from_config(options: Mapping[str, Any] | None) -> str:
    """Read required ``organization_id`` from YAML ``providers[].options``."""
    if not options:
        return ""
    raw = options.get("organization_id")
    return str(raw).strip() if raw is not None else ""
