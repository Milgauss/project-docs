"""API Spend — spend data plane for dashboards."""

from api_spend.client import ApiSpend
from api_spend.config import (
    AppConfig,
    ProviderConfig,
    SyncConfig,
    default_config_path,
    default_store_path,
    ensure_provider_credentials,
    load_config,
    resolve_config_path,
    resolve_store_path,
)
from api_spend.exceptions import (
    ApiSpendError,
    ConfigError,
    CredentialError,
    StoreError,
)
from api_spend.query import V1_QUERY_CURRENCY, iter_bucket_periods, run_query
from api_spend.snapshot_sync import SnapshotSyncResult, run_snapshot_sync
from api_spend.store import DB_FILENAME, SpendStore, default_database_path
from api_spend.models import (
    GapInfo,
    ProviderCapabilities,
    ProviderInfo,
    ProviderSyncStatus,
    ProviderValidation,
    QueryResult,
    SpendBucket,
    SpendRecord,
    Status,
    SyncResult,
    ValidateResult,
)

__all__ = [
    "ApiSpend",
    "V1_QUERY_CURRENCY",
    "iter_bucket_periods",
    "run_query",
    "SnapshotSyncResult",
    "run_snapshot_sync",
    "DB_FILENAME",
    "SpendStore",
    "default_database_path",
    "AppConfig",
    "ProviderConfig",
    "SyncConfig",
    "default_config_path",
    "default_store_path",
    "ensure_provider_credentials",
    "load_config",
    "resolve_config_path",
    "resolve_store_path",
    "ApiSpendError",
    "ConfigError",
    "CredentialError",
    "StoreError",
    "GapInfo",
    "ProviderCapabilities",
    "ProviderInfo",
    "ProviderSyncStatus",
    "ProviderValidation",
    "QueryResult",
    "SpendBucket",
    "SpendRecord",
    "Status",
    "SyncResult",
    "ValidateResult",
]
