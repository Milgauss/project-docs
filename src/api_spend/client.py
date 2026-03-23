"""``ApiSpend`` facade (``PLANNED_INTERFACE.md`` sections 4.3, 5.1–5.6)."""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from api_spend.config import (
    PROVIDER_CREDENTIAL_ENV,
    SNAPSHOT_PROVIDERS,
    AppConfig,
    ProviderConfig,
    load_config,
)
from api_spend.exceptions import ConfigError, CredentialError
from api_spend.models import (
    ProviderCapabilities,
    ProviderInfo,
    ProviderSyncStatus,
    ProviderValidation,
    QueryResult,
    Status,
    SyncResult,
    ValidateResult,
)
from api_spend.providers import get_provider_class
from api_spend.providers.base import BillingApiProvider, SnapshotProvider
from api_spend.providers.openai import OpenAIBillingProvider, openai_options_from_config
from api_spend.providers.anthropic import AnthropicBillingProvider
from api_spend.providers.brightdata import BrightDataBillingProvider
from api_spend.providers.resend import ResendSnapshotProvider
from api_spend.providers.brave import BraveSnapshotProvider
from api_spend.query import run_query
from api_spend.snapshot_sync import run_snapshot_sync
from api_spend.store import DB_FILENAME, SpendStore, default_database_path

logger = logging.getLogger(__name__)

# Snapshot ``SpendRecord.service`` (``D-PROVIDER-CAPS-V1`` / contract §5.1).
SNAPSHOT_SERVICE_BY_PROVIDER: dict[str, str] = {
    "resend": "emails",
    "brave_search": "requests",
}


def _static_capabilities(name: str) -> ProviderCapabilities:
    if name in SNAPSHOT_PROVIDERS:
        return ProviderCapabilities(
            supports_date_range=False,
            native_granularity="snapshot",
            supports_service_breakdown=True,
        )
    return ProviderCapabilities(
        supports_date_range=True,
        native_granularity="day",
        supports_service_breakdown=True,
    )


def _billing_window(
    *,
    end_date: date,
    lookback_days: int,
    previous_latest: date | None,
) -> tuple[date, date]:
    """Return ``(start, end)`` half-open UTC calendar dates for ``fetch_costs``."""
    end = end_date
    if previous_latest is None:
        start = end_date - timedelta(days=lookback_days)
    else:
        start = previous_latest + timedelta(days=1)
    return start, end


def _billing_latest_after_success(
    *,
    end_date: date,
    previous_latest: date | None,
) -> date:
    coverage_end = end_date - timedelta(days=1)
    if previous_latest is None:
        return coverage_end
    return max(previous_latest, coverage_end)


def _provider_config_ok(pc: ProviderConfig) -> tuple[bool, str | None]:
    if pc.name == "openai":
        oid = openai_options_from_config(pc.options)
        if not oid:
            return False, "openai requires options.organization_id in config"
    if pc.name == "brightdata":
        z = str(pc.options.get("zone", "")).strip()
        if not z:
            return False, "brightdata requires options.zone in config"
    return True, None


def _make_billing_provider(
    pc: ProviderConfig,
    *,
    http_client: httpx.Client | None,
) -> BillingApiProvider:
    env = PROVIDER_CREDENTIAL_ENV[pc.name]
    key = os.environ.get(env, "").strip()
    kw: dict[str, Any] = {"api_key": key}
    if http_client is not None:
        kw["client"] = http_client
    if pc.name == "openai":
        return OpenAIBillingProvider(
            organization_id=openai_options_from_config(pc.options),
            **kw,
        )
    if pc.name == "anthropic":
        return AnthropicBillingProvider(**kw)
    if pc.name == "brightdata":
        zone = str(pc.options.get("zone", "")).strip()
        return BrightDataBillingProvider(zone=zone, **kw)
    raise ValueError(f"not a billing provider: {pc.name!r}")


def _make_snapshot_provider(
    pc: ProviderConfig,
    *,
    http_client: httpx.Client | None,
) -> SnapshotProvider:
    env = PROVIDER_CREDENTIAL_ENV[pc.name]
    key = os.environ.get(env, "").strip()
    if pc.name == "resend":
        return ResendSnapshotProvider.from_config(
            key, pc.options, client=http_client
        )
    if pc.name == "brave_search":
        return BraveSnapshotProvider(key, client=http_client)
    raise ValueError(f"not a snapshot provider: {pc.name!r}")


class ApiSpend:
    """High-level API: config, store, sync, query, validate, reset."""

    def __init__(
        self,
        config_path: str | Path | None = None,
        *,
        store: SpendStore | None = None,
        require_credentials: bool = True,
        http_client: httpx.Client | None = None,
    ) -> None:
        """
        ``store``: optional injected store (tests). Default: open ``default_database_path()``.

        ``http_client``: optional shared ``httpx.Client`` for all adapters (integration tests
        with ``MockTransport``).

        ``require_credentials``: passed through to ``load_config`` (default ``True``).
        """
        self._config, self._config_path = load_config(
            config_path,
            require_credentials=require_credentials,
        )
        self._owns_store = store is None
        self._store = store or SpendStore.open(default_database_path())
        self._http_client = http_client
        self._provider_names = [p.name for p in self._config.providers]
        logger.info(
            "ApiSpend initialized config_path=%s configured_providers=%d",
            self._config_path,
            len(self._provider_names),
        )

    @property
    def config(self) -> AppConfig:
        return self._config

    @property
    def config_path(self) -> Path:
        return self._config_path

    @property
    def store(self) -> SpendStore:
        return self._store

    def close(self) -> None:
        if self._owns_store:
            self._store.close()

    def __enter__(self) -> ApiSpend:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _configured_provider_names(self) -> list[str]:
        return list(self._provider_names)

    def sync(self, providers: list[str] | None = None) -> SyncResult:
        synced_at = datetime.now(timezone.utc)
        end_date = synced_at.date()
        target = self._configured_provider_names()
        if providers is not None:
            allowed = frozenset(target)
            for p in providers:
                if p not in allowed:
                    raise ValueError(f"provider {p!r} is not in configured providers")
            target = list(providers)

        logger.info("sync started provider_count=%d", len(target))
        statuses: list[ProviderSyncStatus] = []
        for name in target:
            pc = next(p for p in self._config.providers if p.name == name)
            if pc.name in SNAPSHOT_PROVIDERS:
                statuses.append(self._sync_snapshot(pc, synced_at))
            else:
                statuses.append(
                    self._sync_billing(pc, synced_at, end_date),
                )
        ok_n = sum(1 for s in statuses if s.ok)
        logger.info(
            "sync complete synced_at=%s ok=%d failed=%d",
            synced_at.isoformat(),
            ok_n,
            len(statuses) - ok_n,
        )
        for s in statuses:
            if s.ok:
                logger.debug(
                    "sync provider=%s ok records_added=%d",
                    s.provider,
                    s.records_added,
                )
            else:
                logger.info("sync provider=%s failed", s.provider)
                if s.error:
                    logger.debug("sync provider=%s error=%s", s.provider, s.error)
        return SyncResult(providers=statuses, synced_at=synced_at)

    def _sync_billing(self, pc: ProviderConfig, synced_at: datetime, end_date: date) -> ProviderSyncStatus:
        meta = self._store.get_sync_metadata(pc.name)
        prev_latest = meta[1] if meta else None
        start, end = _billing_window(
            end_date=end_date,
            lookback_days=self._config.sync.lookback_days,
            previous_latest=prev_latest,
        )
        provider = _make_billing_provider(pc, http_client=self._http_client)
        try:
            if end <= start:
                new_latest = _billing_latest_after_success(
                    end_date=end_date,
                    previous_latest=prev_latest,
                )
                self._store.set_sync_metadata(pc.name, synced_at, new_latest)
                return ProviderSyncStatus(
                    provider=pc.name,
                    ok=True,
                    records_added=0,
                    latest_date=new_latest,
                    error=None,
                )
            result = provider.fetch_costs(start, end)
            if result.error:
                logger.debug(
                    "billing fetch provider=%s window=%s..%s error=%s",
                    pc.name,
                    start,
                    end,
                    result.error,
                )
                return ProviderSyncStatus(
                    provider=pc.name,
                    ok=False,
                    records_added=0,
                    latest_date=prev_latest,
                    error=result.error,
                )
            self._store.upsert_spend_records(result.records)
            new_latest = _billing_latest_after_success(
                end_date=end_date,
                previous_latest=prev_latest,
            )
            self._store.set_sync_metadata(pc.name, synced_at, new_latest)
            return ProviderSyncStatus(
                provider=pc.name,
                ok=True,
                records_added=len(result.records),
                latest_date=new_latest,
                error=None,
            )
        finally:
            provider.close()

    def _sync_snapshot(self, pc: ProviderConfig, synced_at: datetime) -> ProviderSyncStatus:
        service = SNAPSHOT_SERVICE_BY_PROVIDER[pc.name]
        provider = _make_snapshot_provider(pc, http_client=self._http_client)
        try:
            meta_before = self._store.get_sync_metadata(pc.name)
            prev_latest = meta_before[1] if meta_before else None
            ss = run_snapshot_sync(
                self._store,
                pc.name,
                service,
                provider,
                synced_at,
            )
            if ss.error:
                return ProviderSyncStatus(
                    provider=pc.name,
                    ok=False,
                    records_added=0,
                    latest_date=prev_latest,
                    error=ss.error,
                    counter_observed=ss.counter_observed,
                )
            meta_after = self._store.get_sync_metadata(pc.name)
            new_latest = meta_after[1] if meta_after else prev_latest
            return ProviderSyncStatus(
                provider=pc.name,
                ok=True,
                records_added=len(ss.records),
                latest_date=new_latest,
                error=None,
                counter_observed=ss.counter_observed,
            )
        finally:
            provider.close()

    def query(
        self,
        start: date,
        end: date,
        *,
        granularity: Literal["day", "week", "month"] = "day",
        providers: list[str] | None = None,
        group_by: str | list[str] | None = None,
    ) -> QueryResult:
        if not self._provider_names:
            raise ValueError("configured_providers must be non-empty")
        logger.debug(
            "query start=%s end=%s granularity=%s",
            start,
            end,
            granularity,
        )
        return run_query(
            self._store,
            start,
            end,
            granularity=granularity,
            configured_providers=self._configured_provider_names(),
            providers=providers,
            group_by=group_by,
        )

    def providers(self) -> list[ProviderInfo]:
        out: list[ProviderInfo] = []
        for pc in self._config.providers:
            meta = self._store.get_sync_metadata(pc.name)
            earliest, latest = self._store.provider_spend_date_bounds(pc.name)
            out.append(
                ProviderInfo(
                    name=pc.name,
                    configured=True,
                    last_synced=meta[0] if meta else None,
                    earliest_data=earliest,
                    latest_data=latest,
                    capabilities=_static_capabilities(pc.name),
                )
            )
        return out

    def status(self) -> Status:
        names = self._configured_provider_names()
        synced_n = 0
        last_sync: datetime | None = None
        for name in names:
            meta = self._store.get_sync_metadata(name)
            if meta:
                synced_n += 1
                ts = meta[0]
                if last_sync is None or ts > last_sync:
                    last_sync = ts
        size: int | None
        if self._store.is_memory_database():
            size = None
        else:
            size = self._store.approximate_size_bytes()
        return Status(
            configured_providers=len(names),
            synced_providers=synced_n,
            last_sync=last_sync,
            store_size_bytes=size,
        )

    def validate(self, *, check_connectivity: bool = False) -> ValidateResult:
        logger.debug("validate check_connectivity=%s", check_connectivity)
        rows: list[ProviderValidation] = []
        for pc in self._config.providers:
            cfg_ok, cfg_err = _provider_config_ok(pc)
            env_var = PROVIDER_CREDENTIAL_ENV[pc.name]
            cred_ok = bool(os.environ.get(env_var, "").strip())
            err_parts: list[str] = []
            if not cfg_ok and cfg_err:
                err_parts.append(cfg_err)
            if not cred_ok:
                err_parts.append(f"missing or empty {env_var}")
            row_err = "; ".join(err_parts) if err_parts else None
            reachable: bool | None = None
            if check_connectivity and cfg_ok and cred_ok:
                try:
                    if pc.name in SNAPSHOT_PROVIDERS:
                        prov = _make_snapshot_provider(
                            pc, http_client=self._http_client
                        )
                    else:
                        prov = _make_billing_provider(
                            pc, http_client=self._http_client
                        )
                    try:
                        reachable = prov.validate_credentials()
                    finally:
                        prov.close()
                except Exception as exc:
                    reachable = False
                    row_err = (row_err + "; " if row_err else "") + str(exc)
            elif not check_connectivity:
                reachable = None
            else:
                reachable = False
            rows.append(
                ProviderValidation(
                    provider=pc.name,
                    config_ok=cfg_ok,
                    credentials_ok=cred_ok,
                    reachable=reachable,
                    error=row_err,
                )
            )
        return ValidateResult(
            providers=rows,
            config_path=str(self._config_path),
        )

    def reset(self, providers: list[str] | None = None) -> None:
        logger.info(
            "reset requested %s",
            "all" if providers is None else f"providers={providers!r}",
        )
        self._store.reset(providers)
