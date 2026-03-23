"""Phase 9.2 contract alignment: models, env vars, exceptions, empty-store query (``TODO.md``)."""

from __future__ import annotations

from datetime import date

import pytest

import api_spend
from api_spend.config import PROVIDER_CREDENTIAL_ENV
from api_spend.exceptions import ApiSpendError, ConfigError, CredentialError, StoreError
from api_spend.http_raw_dump import (
    ANTHROPIC_RAW_RESPONSE_ENV,
    BRAVE_RAW_RESPONSE_ENV,
    BRIGHTDATA_RAW_RESPONSE_ENV,
    OPENAI_RAW_RESPONSE_ENV,
    RESEND_RAW_RESPONSE_ENV,
)
from api_spend.query import run_query
from api_spend.store import SpendStore
from pydantic import BaseModel

# Keep in sync with ``PLANNED_INTERFACE.md`` §8.1–§8.2 (runtime reads in ``src/api_spend``).
_DOCUMENTED_RUNTIME_ENV_VARS = frozenset(
    {
        "API_SPEND_CONFIG",
        "API_SPEND_STORE_PATH",
        *PROVIDER_CREDENTIAL_ENV.values(),
        OPENAI_RAW_RESPONSE_ENV,
        ANTHROPIC_RAW_RESPONSE_ENV,
        BRIGHTDATA_RAW_RESPONSE_ENV,
        RESEND_RAW_RESPONSE_ENV,
        BRAVE_RAW_RESPONSE_ENV,
    }
)

# Public ``BaseModel`` field names (``PLANNED_INTERFACE.md`` §5–§6, §4.2 config models).
_CONTRACT_MODEL_FIELDS: dict[str, frozenset[str]] = {
    "AppConfig": frozenset({"sync", "providers"}),
    "GapInfo": frozenset({"provider", "start", "end", "reason"}),
    "ProviderCapabilities": frozenset(
        {"supports_date_range", "native_granularity", "supports_service_breakdown"}
    ),
    "ProviderConfig": frozenset({"name", "options"}),
    "ProviderInfo": frozenset(
        {
            "name",
            "configured",
            "last_synced",
            "earliest_data",
            "latest_data",
            "capabilities",
        }
    ),
    "ProviderSyncStatus": frozenset(
        {
            "provider",
            "ok",
            "records_added",
            "latest_date",
            "error",
            "counter_observed",
        }
    ),
    "ProviderValidation": frozenset(
        {"provider", "config_ok", "credentials_ok", "reachable", "error"}
    ),
    "QueryResult": frozenset({"buckets", "providers_included", "gaps"}),
    "SpendBucket": frozenset(
        {"period_start", "period_end", "group", "amount", "currency", "coverage"}
    ),
    "SpendRecord": frozenset({"provider", "service", "date", "amount", "currency"}),
    "Status": frozenset(
        {"configured_providers", "synced_providers", "last_sync", "store_size_bytes"}
    ),
    "SyncConfig": frozenset({"lookback_days"}),
    "SyncResult": frozenset({"providers", "synced_at"}),
    "ValidateResult": frozenset({"providers", "config_path"}),
}


def test_code_read_env_vars_are_documented_in_contract_table() -> None:
    assert (
        frozenset(PROVIDER_CREDENTIAL_ENV.values()) <= _DOCUMENTED_RUNTIME_ENV_VARS
    )
    assert {OPENAI_RAW_RESPONSE_ENV, BRAVE_RAW_RESPONSE_ENV} <= _DOCUMENTED_RUNTIME_ENV_VARS
    # Single source for “what src reads” is the §8 table + this test’s expected set.
    used = frozenset(
        {
            "API_SPEND_CONFIG",
            "API_SPEND_STORE_PATH",
            *PROVIDER_CREDENTIAL_ENV.values(),
            OPENAI_RAW_RESPONSE_ENV,
            ANTHROPIC_RAW_RESPONSE_ENV,
            BRIGHTDATA_RAW_RESPONSE_ENV,
            RESEND_RAW_RESPONSE_ENV,
            BRAVE_RAW_RESPONSE_ENV,
        }
    )
    assert used == _DOCUMENTED_RUNTIME_ENV_VARS


def test_public_base_model_fields_match_contract_map() -> None:
    mapped = frozenset(_CONTRACT_MODEL_FIELDS)
    for name in sorted(api_spend.__all__):
        obj = getattr(api_spend, name)
        if not isinstance(obj, type) or not issubclass(obj, BaseModel):
            continue
        if obj is BaseModel:
            continue
        assert name in mapped, f"add {name} to _CONTRACT_MODEL_FIELDS in test_phase9_contract.py"
        fields = frozenset(obj.model_fields)
        assert fields == _CONTRACT_MODEL_FIELDS[name], (
            f"{name}: expected {_CONTRACT_MODEL_FIELDS[name]}, got {fields}"
        )


def test_api_spend_error_subclasses_inherit_base() -> None:
    for cls in (ConfigError, CredentialError, StoreError):
        assert issubclass(cls, ApiSpendError)


def test_run_query_end_before_start_raises_value_error(store: SpendStore) -> None:
    with pytest.raises(ValueError, match="end must be after start"):
        run_query(
            store,
            date(2025, 1, 5),
            date(2025, 1, 1),
            configured_providers=["openai"],
        )


def test_run_query_unknown_provider_subset_raises_value_error(store: SpendStore) -> None:
    with pytest.raises(ValueError, match="not in configured_providers"):
        run_query(
            store,
            date(2025, 1, 1),
            date(2025, 1, 2),
            configured_providers=["openai"],
            providers=["anthropic"],
        )


def test_query_empty_store_partial_coverage_and_full_gaps() -> None:
    store = SpendStore.open(":memory:")
    try:
        start, end = date(2025, 1, 1), date(2025, 1, 4)
        r = run_query(
            store,
            start,
            end,
            granularity="day",
            configured_providers=["openai", "anthropic"],
            group_by=None,
        )
        assert r.providers_included == ["anthropic", "openai"]
        assert len(r.buckets) == 3
        assert all(b.amount == 0 for b in r.buckets)
        assert all(b.coverage == "partial" for b in r.buckets)
        assert len(r.gaps) == 2
        gap_providers = {g.provider for g in r.gaps}
        assert gap_providers == {"anthropic", "openai"}
        for g in r.gaps:
            assert g.start == start
            assert g.end == end
            assert "no spend data" in g.reason.lower()
    finally:
        store.close()


@pytest.fixture
def store() -> SpendStore:
    s = SpendStore.open(":memory:")
    yield s
    s.close()
