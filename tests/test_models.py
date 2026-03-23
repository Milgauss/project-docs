"""Contract models: construct and ``model_dump`` round-trip."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from api_spend import models


def _roundtrip(model_cls, **data):
    instance = model_cls(**data)
    restored = model_cls.model_validate(instance.model_dump())
    assert restored == instance
    return instance


def test_spend_record_roundtrip():
    _roundtrip(
        models.SpendRecord,
        provider="openai",
        service="gpt-4o",
        date=date(2025, 1, 15),
        amount=Decimal("12.34"),
        currency="USD",
    )


def test_provider_sync_status_roundtrip():
    _roundtrip(
        models.ProviderSyncStatus,
        provider="openai",
        ok=True,
        records_added=3,
        latest_date=date(2025, 1, 20),
        error=None,
    )


def test_provider_sync_status_snapshot_counter_roundtrip():
    _roundtrip(
        models.ProviderSyncStatus,
        provider="resend",
        ok=True,
        records_added=0,
        latest_date=None,
        error=None,
        counter_observed=5,
    )


def test_sync_result_roundtrip():
    _roundtrip(
        models.SyncResult,
        providers=[
            models.ProviderSyncStatus(
                provider="openai",
                ok=True,
                records_added=1,
                latest_date=date(2025, 1, 1),
                error=None,
            )
        ],
        synced_at=datetime(2025, 1, 21, 15, 30, 0),
    )


@pytest.mark.parametrize(
    "coverage",
    ["complete", "partial", "estimated"],
)
def test_spend_bucket_roundtrip(coverage):
    _roundtrip(
        models.SpendBucket,
        period_start=date(2025, 1, 1),
        period_end=date(2025, 1, 2),
        group={"provider": "openai"},
        amount=Decimal("0"),
        currency="USD",
        coverage=coverage,
    )


def test_gap_info_roundtrip():
    _roundtrip(
        models.GapInfo,
        provider="anthropic",
        start=date(2025, 2, 1),
        end=date(2025, 2, 15),
        reason="provider not synced before 2025-02-15",
    )


def test_query_result_roundtrip():
    _roundtrip(
        models.QueryResult,
        buckets=[
            models.SpendBucket(
                period_start=date(2025, 1, 1),
                period_end=date(2025, 1, 2),
                group=None,
                amount=Decimal("10.00"),
                currency="USD",
                coverage="complete",
            )
        ],
        providers_included=["openai"],
        gaps=[],
    )


def test_provider_capabilities_and_info_roundtrip():
    caps = models.ProviderCapabilities(
        supports_date_range=True,
        native_granularity="day",
        supports_service_breakdown=True,
    )
    _roundtrip(
        models.ProviderInfo,
        name="openai",
        configured=True,
        last_synced=datetime(2025, 1, 1, 0, 0, 0),
        earliest_data=date(2024, 12, 1),
        latest_data=date(2025, 1, 1),
        capabilities=caps,
    )


def test_status_roundtrip():
    _roundtrip(
        models.Status,
        configured_providers=2,
        synced_providers=1,
        last_sync=datetime(2025, 1, 1, 12, 0, 0),
        store_size_bytes=4096,
    )


def test_provider_validation_and_validate_result_roundtrip():
    pv = models.ProviderValidation(
        provider="resend",
        config_ok=True,
        credentials_ok=True,
        reachable=None,
        error=None,
    )
    _roundtrip(
        models.ValidateResult,
        providers=[pv],
        config_path="/home/user/.config/api-spend/config.yaml",
    )


def test_import_api_spend_public_surface():
    import api_spend

    assert api_spend.ConfigError.__bases__ == (api_spend.ApiSpendError,)
    assert api_spend.SpendRecord is models.SpendRecord
    assert callable(api_spend.run_query)
    assert api_spend.V1_QUERY_CURRENCY == "USD"
