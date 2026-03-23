"""Public Pydantic models (``PLANNED_INTERFACE.md`` §5–§6)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SpendRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    service: str
    date: date
    amount: Decimal
    currency: str


class ProviderSyncStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    ok: bool
    records_added: int
    latest_date: date | None
    error: str | None
    # Snapshot providers (Resend, Brave): vendor counter from this sync; billing: None.
    counter_observed: int | None = None


class SyncResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    providers: list[ProviderSyncStatus]
    synced_at: datetime


class SpendBucket(BaseModel):
    model_config = ConfigDict(frozen=True)

    period_start: date
    period_end: date
    group: dict[str, str] | None
    amount: Decimal
    currency: str
    coverage: Literal["complete", "partial", "estimated"]


class GapInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    start: date
    end: date
    reason: str


class QueryResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    buckets: list[SpendBucket]
    providers_included: list[str]
    gaps: list[GapInfo]


class ProviderCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True)

    supports_date_range: bool
    native_granularity: str
    supports_service_breakdown: bool


class ProviderInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    configured: bool
    last_synced: datetime | None
    earliest_data: date | None
    latest_data: date | None
    capabilities: ProviderCapabilities


class Status(BaseModel):
    model_config = ConfigDict(frozen=True)

    configured_providers: int
    synced_providers: int
    last_sync: datetime | None
    store_size_bytes: int | None


class ProviderValidation(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    config_ok: bool
    credentials_ok: bool
    reachable: bool | None
    error: str | None


class ValidateResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    providers: list[ProviderValidation]
    config_path: str
