"""Provider abstract bases (``IMPLEMENTATION_PLAN.md`` §3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from api_spend.models import SpendRecord


def utc_quota_period_month(recorded_at: datetime) -> str:
    """UTC ``YYYY-MM`` — default snapshot quota key for monthly windows."""
    dt = recorded_at
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return f"{dt.year:04d}-{dt.month:02d}"


def utc_quota_period_day(recorded_at: datetime) -> str:
    """UTC calendar date as ``YYYY-MM-DD`` — quota key when the counter resets daily."""
    dt = recorded_at
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).date().isoformat()


@dataclass(frozen=True)
class FetchCostsResult:
    """Outcome of a billing-API cost fetch (``TODO.md`` Phase 5 — in-band errors)."""

    records: list[SpendRecord]
    error: str | None


class BillingApiProvider(ABC):
    """Provider with date-range cost reporting (``PLANNED_INTERFACE.md`` §3.1)."""

    @abstractmethod
    def fetch_costs(self, start: date, end: date) -> FetchCostsResult:
        """Load costs for ``[start, end)`` (half-open calendar dates, UTC day boundaries).

        On API failure, return ``FetchCostsResult([], error=...)`` — do not raise for
        provider or HTTP error responses.
        """

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Return ``True`` if credentials allow a minimal read-only API call."""


class SnapshotProvider(ABC):
    """Usage counter + estimate pricing (``PLANNED_INTERFACE.md`` §3.2)."""

    @abstractmethod
    def read_counter(self) -> int:
        """Current usage counter from provider (e.g. monthly or daily quota usage)."""

    def sync_quota_period(self, recorded_at: datetime) -> str:
        """Stable period key for comparing snapshots (rollover when this string changes)."""
        return utc_quota_period_month(recorded_at)

    @abstractmethod
    def estimate_cost(self, usage_delta: int) -> Decimal:
        """Cost in USD for ``usage_delta`` units since last snapshot."""

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Return ``True`` if credentials allow a minimal read-only API call."""
