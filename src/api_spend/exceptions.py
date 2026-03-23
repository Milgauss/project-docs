"""Public exception hierarchy (``PLANNED_INTERFACE.md`` §7)."""


class ApiSpendError(Exception):
    """Base for all package errors."""


class ConfigError(ApiSpendError):
    """Config file missing, unparseable, or invalid."""


class CredentialError(ApiSpendError):
    """Required credential (e.g. env var) missing."""


class StoreError(ApiSpendError):
    """Local data store cannot be opened or is corrupted."""
