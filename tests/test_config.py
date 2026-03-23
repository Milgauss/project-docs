"""Config loading, path resolution, and credential checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from api_spend import AppConfig, ConfigError, CredentialError, load_config, resolve_config_path
from api_spend.config import (
    default_config_path,
    default_store_path,
    ensure_provider_credentials,
    resolve_store_path,
)


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_valid_yaml_loads_and_fields_match(tmp_path, monkeypatch):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        """
sync:
  lookback_days: 42
providers:
  - name: openai
  - name: resend
    options:
      plan: pro
""",
    )
    monkeypatch.setenv("API_SPEND_OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("API_SPEND_RESEND_API_KEY", "re_test")

    cfg, resolved = load_config(cfg_path, require_credentials=True)

    assert resolved == cfg_path.resolve()
    assert cfg.sync.lookback_days == 42
    assert len(cfg.providers) == 2
    assert cfg.providers[0].name == "openai"
    assert cfg.providers[0].options == {}
    assert cfg.providers[1].name == "resend"
    assert cfg.providers[1].options == {"plan": "pro"}


def test_missing_config_file_raises_config_error(tmp_path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(ConfigError, match="not found"):
        load_config(missing, require_credentials=False)


def test_malformed_yaml_raises_config_error(tmp_path):
    bad = _write(tmp_path / "bad.yaml", "{ not valid yaml [[[\n")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_config(bad, require_credentials=False)


def test_non_mapping_top_level_raises_config_error(tmp_path):
    bad = _write(tmp_path / "list.yaml", "- foo\n")
    with pytest.raises(ConfigError, match="mapping"):
        load_config(bad, require_credentials=False)


def test_unknown_provider_raises_config_error(tmp_path):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        "providers:\n  - name: unknown_vendor\n",
    )
    with pytest.raises(ConfigError, match="unknown provider"):
        load_config(cfg_path, require_credentials=False)


def test_missing_env_var_raises_credential_error(tmp_path, monkeypatch):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        "providers:\n  - name: anthropic\n",
    )
    monkeypatch.delenv("API_SPEND_ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(CredentialError, match="API_SPEND_ANTHROPIC_API_KEY"):
        load_config(cfg_path, require_credentials=True)


def test_api_spend_config_env_overrides_default_path(tmp_path, monkeypatch):
    cfg_file = _write(
        tmp_path / "from-env.yaml",
        "providers:\n  - name: brightdata\n",
    )
    monkeypatch.setenv("API_SPEND_CONFIG", str(cfg_file))
    monkeypatch.setenv("API_SPEND_BRIGHTDATA_API_KEY", "bd-token")

    cfg, resolved = load_config(None, require_credentials=True)

    assert resolved == cfg_file.resolve()
    assert cfg.providers[0].name == "brightdata"


def test_explicit_path_overrides_api_spend_config(tmp_path, monkeypatch):
    ignored = _write(tmp_path / "ignored.yaml", "providers:\n  - name: openai\n")
    used = _write(tmp_path / "used.yaml", "providers:\n  - name: openai\n")
    monkeypatch.setenv("API_SPEND_CONFIG", str(ignored))
    monkeypatch.setenv("API_SPEND_OPENAI_API_KEY", "sk")

    _, resolved = load_config(used, require_credentials=True)
    assert resolved == used.resolve()


def test_sync_lookback_defaults_to_60_when_omitted(tmp_path, monkeypatch):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        "providers:\n  - name: openai\n",
    )
    monkeypatch.setenv("API_SPEND_OPENAI_API_KEY", "sk")

    cfg, _ = load_config(cfg_path, require_credentials=True)
    assert cfg.sync.lookback_days == 60


def test_empty_top_level_yaml_mapping_from_none_document(tmp_path, monkeypatch):
    """Empty file → safe_load None; treated as empty mapping, defaults applied."""
    cfg_path = _write(tmp_path / "empty.yaml", "")
    monkeypatch.delenv("API_SPEND_OPENAI_API_KEY", raising=False)
    cfg, _ = load_config(cfg_path, require_credentials=False)
    assert cfg == AppConfig()
    assert cfg.providers == []


def test_resolve_config_path_uses_default_when_no_env(monkeypatch):
    monkeypatch.delenv("API_SPEND_CONFIG", raising=False)
    p = resolve_config_path(None)
    assert p == default_config_path()


def test_resolve_store_path_uses_default_when_no_env(monkeypatch):
    monkeypatch.delenv("API_SPEND_STORE_PATH", raising=False)
    p = resolve_store_path(None)
    assert p == default_store_path()
    assert p == Path.home() / ".local" / "share" / "api-spend"


def test_resolve_store_path_env_override(tmp_path, monkeypatch):
    custom = tmp_path / "custom-store"
    monkeypatch.setenv("API_SPEND_STORE_PATH", str(custom))
    assert resolve_store_path(None) == custom.resolve()


def test_resolve_store_path_explicit_overrides_env(tmp_path, monkeypatch):
    ignored = tmp_path / "ignored"
    used = tmp_path / "used"
    monkeypatch.setenv("API_SPEND_STORE_PATH", str(ignored))
    assert resolve_store_path(used) == used.resolve()


def test_ensure_provider_credentials_empty_config_ok():
    ensure_provider_credentials(AppConfig())


def test_blank_env_var_treated_as_missing(tmp_path, monkeypatch):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        "providers:\n  - name: brave_search\n",
    )
    monkeypatch.setenv("API_SPEND_BRAVE_API_KEY", "   ")
    with pytest.raises(CredentialError):
        load_config(cfg_path, require_credentials=True)


def test_load_config_without_require_credentials_skips_env(tmp_path, monkeypatch):
    cfg_path = _write(
        tmp_path / "cfg.yaml",
        "providers:\n  - name: openai\n",
    )
    monkeypatch.delenv("API_SPEND_OPENAI_API_KEY", raising=False)
    cfg, _ = load_config(cfg_path, require_credentials=False)
    assert cfg.providers[0].name == "openai"
