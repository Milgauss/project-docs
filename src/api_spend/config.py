"""Config file loading and path helpers (``PLANNED_INTERFACE.md`` §4.2, §8)."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Final

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from api_spend.exceptions import ConfigError, CredentialError

logger = logging.getLogger(__name__)

KNOWN_PROVIDERS: Final[frozenset[str]] = frozenset(
    {
        "openai",
        "anthropic",
        "brightdata",
        "resend",
        "brave_search",
    }
)

# Snapshot-based providers (`PLANNED_INTERFACE.md` §3.2) — query uses this for ``coverage``.
SNAPSHOT_PROVIDERS: Final[frozenset[str]] = frozenset({"resend", "brave_search"})

# Config ``name`` → credential env var (not a mechanical ``API_SPEND_{NAME}_API_KEY``; see §8).
PROVIDER_CREDENTIAL_ENV: Final[dict[str, str]] = {
    "openai": "API_SPEND_OPENAI_API_KEY",
    "anthropic": "API_SPEND_ANTHROPIC_API_KEY",
    "brightdata": "API_SPEND_BRIGHTDATA_API_KEY",
    "resend": "API_SPEND_RESEND_API_KEY",
    "brave_search": "API_SPEND_BRAVE_API_KEY",
}


class SyncConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    lookback_days: int = Field(default=60, ge=1)


class ProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    options: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def name_must_be_known(cls, v: str) -> str:
        if v not in KNOWN_PROVIDERS:
            raise ValueError(f"unknown provider {v!r}; expected one of {sorted(KNOWN_PROVIDERS)}")
        return v


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    sync: SyncConfig = Field(default_factory=SyncConfig)
    providers: list[ProviderConfig] = Field(default_factory=list)


def default_config_path() -> Path:
    """Default config path when no explicit path or ``API_SPEND_CONFIG`` is set."""
    return Path.home() / ".config" / "api-spend" / "config.yaml"


def resolve_config_path(explicit: str | Path | None = None) -> Path:
    """Resolve path: explicit argument wins, then ``API_SPEND_CONFIG``, then default."""
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env_path = os.environ.get("API_SPEND_CONFIG")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return default_config_path()


def default_store_path() -> Path:
    """Default **directory** for the local SQLite store (``API_SPEND_STORE_PATH`` overrides)."""
    return Path.home() / ".local" / "share" / "api-spend"


def resolve_store_path(explicit: str | Path | None = None) -> Path:
    """
    Resolve the store **root directory**: explicit argument, then ``API_SPEND_STORE_PATH``, then
    ``default_store_path()``. The database file lives inside this directory (see Phase 3 ``store``).
    """
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env_path = os.environ.get("API_SPEND_STORE_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return default_store_path()


def _format_validation_error(err: ValidationError) -> str:
    parts: list[str] = []
    for e in err.errors(include_url=False):
        loc = ".".join(str(x) for x in e.get("loc", ()))
        parts.append(f"{loc}: {e.get('msg', 'validation error')}")
    return "; ".join(parts) if parts else "invalid configuration"


def load_config(
    config_path: str | Path | None = None,
    *,
    require_credentials: bool = True,
) -> tuple[AppConfig, Path]:
    """
    Load YAML from disk, validate shape, optionally require provider credential env vars.

    ``require_credentials=False`` is intended for **tests** and **YAML-only validation** without
    setting env vars. Do **not** use ``False`` on production code paths (e.g. ``ApiSpend``)
    unless the contract explicitly allows it.

    Returns ``(config, resolved_path)`` for use as ``ValidateResult.config_path`` and logging.
    """
    path = resolve_config_path(config_path)
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot read config file {path}: {exc}") from exc

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in config file {path}: {exc}") from exc

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(
            f"config file must contain a YAML mapping at the top level, got {type(data).__name__}"
        )

    try:
        config = AppConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(_format_validation_error(exc)) from exc

    if require_credentials:
        ensure_provider_credentials(config)

    logger.debug(
        "loaded config path=%s providers=%d",
        path,
        len(config.providers),
    )
    return config, path


def ensure_provider_credentials(config: AppConfig) -> None:
    """Raise ``CredentialError`` if any configured provider's API key env var is missing or blank."""
    for provider in config.providers:
        env_var = PROVIDER_CREDENTIAL_ENV[provider.name]
        value = os.environ.get(env_var, "")
        if not value.strip():
            raise CredentialError(
                f"environment variable {env_var} is not set or empty "
                f"(required for configured provider {provider.name!r})"
            )
