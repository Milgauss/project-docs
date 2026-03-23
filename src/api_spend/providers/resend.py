"""Resend snapshot adapter — ``GET /emails`` + quota headers (``PLANNED_INTERFACE.md`` section 3.2)."""

from __future__ import annotations

import time
from collections.abc import Mapping
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from api_spend.http_raw_dump import RESEND_RAW_RESPONSE_ENV, maybe_dump_http_response
from api_spend.providers.base import (
    SnapshotProvider,
    utc_quota_period_day,
    utc_quota_period_month,
)

RESEND_API_BASE = "https://api.resend.com"
LIST_EMAILS_PATH = "/emails"
DEFAULT_TIMEOUT = 60.0
_DEFAULT_USER_AGENT = "api-spend/1.0.0"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _utc_month_bounds(ref: datetime) -> tuple[datetime, datetime]:
    """Start (inclusive) and end (exclusive) of ref's UTC calendar month."""
    dt = ref.astimezone(timezone.utc)
    start = datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)
    if dt.month == 12:
        end = datetime(dt.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(dt.year, dt.month + 1, 1, tzinfo=timezone.utc)
    return start, end


def _parse_resend_created_at(value: str) -> datetime:
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    parsed = datetime.fromisoformat(s)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def resend_options_from_config(options: Mapping[str, Any]) -> tuple[str, Decimal | None]:
    plan = str(options.get("plan", "pro")).strip()
    raw = options.get("per_email_usd")
    per_email: Decimal | None = Decimal(str(raw)) if raw is not None else None
    return plan, per_email


class ResendSnapshotProvider(SnapshotProvider):
    """Reads used email quota from ``GET /emails`` response headers.

    Resend may send **`x-resend-monthly-quota`** (typical on paid) or only **`x-resend-daily-quota`**
    (documented for free tier). When only daily is present, snapshot periods use UTC **calendar days**
    so counter resets align with Resend's daily window.

    Some responses include only IETF **`ratelimit-*`** headers (HTTP request throttling — not email
    quota). In that case the adapter **paginates** ``GET /emails`` and counts list rows whose
    **`created_at`** falls in the **current UTC calendar month**. That can diverge from Resend's
    internal quota if e.g. received-mail counts apply; prefer quota headers when Resend sends them.
    """

    def __init__(
        self,
        api_key: str,
        *,
        plan: str = "pro",
        per_email_usd: Decimal | None = None,
        client: httpx.Client | None = None,
        base_url: str = RESEND_API_BASE,
        raw_response_env: str = RESEND_RAW_RESPONSE_ENV,
    ) -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._raw_env = raw_response_env
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=DEFAULT_TIMEOUT)
        self._quota_header_kind: str = "month"
        plan_norm = plan.strip().lower()
        if per_email_usd is not None:
            self._per_email = Decimal(str(per_email_usd))
        elif plan_norm == "pro":
            self._per_email = Decimal("0.0004")
        elif plan_norm == "free":
            self._per_email = Decimal("0")
        else:
            raise ValueError(
                f"unknown resend plan {plan!r}; use 'pro', 'free', or set per_email_usd in config"
            )

    @classmethod
    def from_config(
        cls,
        api_key: str,
        options: Mapping[str, Any],
        **kwargs: Any,
    ) -> ResendSnapshotProvider:
        plan, per_email = resend_options_from_config(options)
        return cls(api_key, plan=plan, per_email_usd=per_email, **kwargs)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> ResendSnapshotProvider:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def sync_quota_period(self, recorded_at: datetime) -> str:
        if self._quota_header_kind == "day":
            return utc_quota_period_day(recorded_at)
        return utc_quota_period_month(recorded_at)

    def _read_counter_from_list_pages(self, initial: httpx.Response, ref: datetime) -> int:
        """Assume list is newest-first; stop when the oldest row on a page is before the month."""
        month_start, month_end = _utc_month_bounds(ref)

        def in_month(dt: datetime) -> bool:
            return month_start <= dt < month_end

        url = f"{self._base_url}{LIST_EMAILS_PATH}"
        req_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": _DEFAULT_USER_AGENT,
        }

        def page_body(resp: httpx.Response) -> dict[str, Any]:
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                body = (exc.response.text or "")[:800]
                raise ValueError(
                    f"Resend GET /emails HTTP {exc.response.status_code}: {body or exc!s}"
                ) from exc
            raw = resp.json()
            if not isinstance(raw, dict) or raw.get("object") != "list":
                raise ValueError(
                    "Resend GET /emails: expected JSON object with object=='list' for list fallback"
                )
            return raw

        total = 0
        body = page_body(initial)

        while True:
            data = body.get("data")
            if not isinstance(data, list):
                raise ValueError("Resend GET /emails: missing or invalid 'data' array")
            if not data:
                break
            try:
                newest = _parse_resend_created_at(str(data[0]["created_at"]))
                oldest = _parse_resend_created_at(str(data[-1]["created_at"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    "Resend list fallback: each email needs a parseable string 'created_at'"
                ) from exc

            if newest < month_start:
                break
            for item in data:
                if not isinstance(item, dict) or "created_at" not in item:
                    continue
                try:
                    dt = _parse_resend_created_at(str(item["created_at"]))
                except ValueError:
                    continue
                if in_month(dt):
                    total += 1

            has_more = bool(body.get("has_more"))
            if not has_more or oldest < month_start:
                break
            after = data[-1].get("id")
            if not after:
                break
            time.sleep(0.21)
            r = self._client.get(
                url, params={"limit": 100, "after": str(after)}, headers=req_headers
            )
            maybe_dump_http_response(r, self._raw_env)
            body = page_body(r)

        return total

    def read_counter(self) -> int:
        url = f"{self._base_url}{LIST_EMAILS_PATH}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": _DEFAULT_USER_AGENT,
        }
        ref = _now_utc()
        r = self._client.get(url, params={"limit": 100}, headers=headers)
        maybe_dump_http_response(r, self._raw_env)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = (exc.response.text or "")[:800]
            raise ValueError(
                f"Resend GET /emails HTTP {exc.response.status_code}: {body or exc!s}"
            ) from exc

        monthly = r.headers.get("x-resend-monthly-quota")
        daily = r.headers.get("x-resend-daily-quota")
        if monthly is not None:
            self._quota_header_kind = "month"
            return int(str(monthly).strip())
        if daily is not None:
            self._quota_header_kind = "day"
            return int(str(daily).strip())

        self._quota_header_kind = "month"
        return self._read_counter_from_list_pages(r, ref)

    def estimate_cost(self, usage_delta: int) -> Decimal:
        return self._per_email * usage_delta

    def validate_credentials(self) -> bool:
        try:
            self.read_counter()
            return True
        except Exception:
            return False
