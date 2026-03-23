"""``ApiSpend`` facade integration tests (``TODO.md`` Phase 8.2)."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from api_spend import ApiSpend
from api_spend.providers.openai import _date_start_unix_utc
from api_spend.store import SpendStore


def _anchor_day() -> date:
    """Day guaranteed inside default first-sync lookback when sync uses ``date.today()``."""
    return date.today() - timedelta(days=1)


def _write_config(path: Path, *, lookback_days: int = 7) -> None:
    path.write_text(
        f"""sync:
  lookback_days: {lookback_days}
providers:
  - name: openai
    options:
      organization_id: org-test
  - name: anthropic
""",
        encoding="utf-8",
    )


def _openai_fetch_json(anchor: date) -> dict:
    ts = _date_start_unix_utc(anchor)
    return {
        "object": "list",
        "data": [
            {
                "object": "bucket",
                "start_time": ts,
                "end_time": ts + 86400,
                "results": [
                    {
                        "object": "organization.costs.result",
                        "amount": {"value": 2.0, "currency": "usd"},
                        "line_item": "gpt-4o-mini, input",
                        "project_id": "proj_abc",
                    },
                ],
            }
        ],
        "next_page": None,
    }


def _anthropic_fetch_json(anchor: date) -> dict:
    return {
        "data": [
            {
                "starting_at": f"{anchor.isoformat()}T00:00:00Z",
                "results": [
                    {
                        "workspace_id": "ws_1",
                        "model": "claude-3-5-sonnet",
                        "cost_type": "usage",
                        "token_type": "input",
                        "amount": 150,
                        "currency": "USD",
                    },
                ],
            },
        ],
        "has_more": False,
    }


def _make_transport(
    *,
    anchor: date,
    anthropic_fetch_fail: bool = False,
    anthropic_validate_ok: bool = True,
    openai_fetch_fail: bool = False,
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host or ""
        url = str(request.url)
        if host == "api.openai.com":
            if "/organization/costs" not in url:
                return httpx.Response(404)
            if request.url.params.get("limit") == "1":
                return httpx.Response(
                    200, json={"object": "list", "data": [], "next_page": None}
                )
            if openai_fetch_fail:
                return httpx.Response(500, text="openai upstream error")
            return httpx.Response(200, json=_openai_fetch_json(anchor))
        if host == "api.anthropic.com":
            if "/v1/organizations/cost_report" not in url:
                return httpx.Response(404)
            if request.url.params.get("limit") == "1":
                if not anthropic_validate_ok:
                    return httpx.Response(
                        401, json={"error": {"message": "unauthorized"}}
                    )
                return httpx.Response(200, json={"data": [], "has_more": False})
            if anthropic_fetch_fail:
                return httpx.Response(500, text="upstream error")
            return httpx.Response(200, json=_anthropic_fetch_json(anchor))
        return httpx.Response(404, json={"error": f"unexpected host {host!r}"})

    return httpx.MockTransport(handler)


@contextmanager
def _api_spend_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    store: SpendStore | None = None,
    anthropic_fetch_fail: bool = False,
    anthropic_validate_ok: bool = True,
    openai_fetch_fail: bool = False,
    require_credentials: bool = True,
) -> Iterator[tuple[ApiSpend, SpendStore, date]]:
    cfg = tmp_path / "config.yaml"
    _write_config(cfg)
    if require_credentials:
        monkeypatch.setenv("API_SPEND_OPENAI_API_KEY", "sk-admin-openai-test")
        monkeypatch.setenv("API_SPEND_ANTHROPIC_API_KEY", "sk-ant-admin-test")
    anchor = _anchor_day()
    transport = _make_transport(
        anchor=anchor,
        anthropic_fetch_fail=anthropic_fetch_fail,
        anthropic_validate_ok=anthropic_validate_ok,
        openai_fetch_fail=openai_fetch_fail,
    )
    own_store = store is None
    st = store or SpendStore.open(":memory:")
    http = httpx.Client(transport=transport)
    api = ApiSpend(
        cfg,
        store=st,
        require_credentials=require_credentials,
        http_client=http,
    )
    try:
        yield api, st, anchor
    finally:
        http.close()
        api.close()
        if own_store:
            st.close()


def test_validate_default_reachable_none(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, _a):
        vr = api.validate(check_connectivity=False)
        assert {r.provider for r in vr.providers} == {"openai", "anthropic"}
        for r in vr.providers:
            assert r.config_ok and r.credentials_ok
            assert r.reachable is None
            assert r.error is None


def test_validate_check_connectivity_success(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, _a):
        vr = api.validate(check_connectivity=True)
        for r in vr.providers:
            assert r.reachable is True


def test_validate_check_connectivity_unreachable(tmp_path, monkeypatch):
    with _api_spend_session(
        tmp_path, monkeypatch, anthropic_validate_ok=False
    ) as (api, _, _a):
        vr = api.validate(check_connectivity=True)
        by_name = {r.provider: r for r in vr.providers}
        assert by_name["openai"].reachable is True
        assert by_name["anthropic"].reachable is False


def test_validate_without_credentials_optional(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_config(cfg)
    monkeypatch.delenv("API_SPEND_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("API_SPEND_ANTHROPIC_API_KEY", raising=False)
    store = SpendStore.open(":memory:")
    api = ApiSpend(cfg, store=store, require_credentials=False)
    try:
        vr = api.validate(check_connectivity=False)
        for r in vr.providers:
            assert r.credentials_ok is False
            assert r.reachable is None
    finally:
        api.close()
        store.close()


def test_full_lifecycle_validate_sync_query(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, anchor):
        api.validate(check_connectivity=False)
        sr = api.sync()
        assert len(sr.providers) == 2
        assert all(p.ok for p in sr.providers)
        qstart, qend = anchor, anchor + timedelta(days=1)
        qr = api.query(qstart, qend, granularity="day")
        assert qr.providers_included == ["anthropic", "openai"]
        assert sum(b.amount for b in qr.buckets) == Decimal("3.5")


def test_partial_sync_failure(tmp_path, monkeypatch):
    with _api_spend_session(
        tmp_path, monkeypatch, anthropic_fetch_fail=True
    ) as (api, _, _a):
        sr = api.sync()
        by_name = {p.provider: p for p in sr.providers}
        assert by_name["openai"].ok is True
        assert by_name["openai"].records_added >= 1
        assert by_name["anthropic"].ok is False
        assert by_name["anthropic"].error
        assert by_name["anthropic"].records_added == 0


def test_providers_and_status_after_sync(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, anchor):
        synced = api.sync()
        infos = {i.name: i for i in api.providers()}
        assert infos["openai"].last_synced == synced.synced_at
        assert infos["openai"].earliest_data == anchor
        assert infos["openai"].latest_data == anchor
        assert infos["openai"].capabilities.supports_date_range is True
        assert infos["openai"].capabilities.native_granularity == "day"
        st = api.status()
        assert st.configured_providers == 2
        assert st.synced_providers == 2
        assert st.last_sync == synced.synced_at
        assert st.store_size_bytes is None


def test_reset_all_then_query_zeros(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, anchor):
        api.sync()
        api.reset()
        qstart, qend = anchor - timedelta(days=1), anchor + timedelta(days=2)
        qr = api.query(qstart, qend, granularity="day")
        assert all(b.amount == 0 for b in qr.buckets)


def test_reset_single_provider(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, anchor):
        api.sync()
        api.reset(providers=["openai"])
        qstart, qend = anchor, anchor + timedelta(days=1)
        q_openai = api.query(qstart, qend, providers=["openai"])
        assert sum(b.amount for b in q_openai.buckets) == 0
        q_anthropic = api.query(qstart, qend, providers=["anthropic"])
        assert sum(b.amount for b in q_anthropic.buckets) == Decimal("1.5")


def test_group_by_provider_and_service(tmp_path, monkeypatch):
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, anchor):
        api.sync()
        qstart, qend = anchor, anchor + timedelta(days=1)
        qr = api.query(
            qstart,
            qend,
            granularity="day",
            group_by=["provider", "service"],
        )
        triples = {
            (b.group["provider"], b.group["service"], b.amount)
            for b in qr.buckets
            if b.group
        }
        assert ("anthropic", "ws_1:claude-3-5-sonnet:usage:input", Decimal("1.5")) in triples
        assert ("openai", "proj_abc:gpt-4o-mini, input", Decimal("2")) in triples


def test_sync_all_providers_fail_in_band(tmp_path, monkeypatch):
    with _api_spend_session(
        tmp_path,
        monkeypatch,
        openai_fetch_fail=True,
        anthropic_fetch_fail=True,
    ) as (api, _, _a):
        sr = api.sync()
        assert len(sr.providers) == 2
        assert all(not p.ok for p in sr.providers)
        assert all(p.error for p in sr.providers)


def test_query_raises_when_no_configured_providers(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "sync:\n  lookback_days: 7\nproviders: []\n",
        encoding="utf-8",
    )
    store = SpendStore.open(":memory:")
    api = ApiSpend(cfg, store=store, require_credentials=False)
    try:
        with pytest.raises(ValueError, match="configured_providers must be non-empty"):
            api.query(date(2025, 1, 1), date(2025, 1, 2))
        sr = api.sync()
        assert sr.providers == []
    finally:
        api.close()
        store.close()


def test_sync_logs_info_when_logging_configured(tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="api_spend.client")
    with _api_spend_session(tmp_path, monkeypatch) as (api, _, _a):
        api.sync()
    assert any("sync started" in r.message for r in caplog.records)
    assert any("sync complete" in r.message for r in caplog.records)


def test_status_store_size_on_disk(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    _write_config(cfg)
    monkeypatch.setenv("API_SPEND_OPENAI_API_KEY", "sk-admin-openai-test")
    monkeypatch.setenv("API_SPEND_ANTHROPIC_API_KEY", "sk-ant-admin-test")
    db = tmp_path / "t.sqlite"
    store = SpendStore.open(db)
    try:
        with _api_spend_session(tmp_path, monkeypatch, store=store) as (api, _, _a):
            api.sync()
            st = api.status()
            assert st.store_size_bytes is not None
            assert st.store_size_bytes > 0
    finally:
        store.close()
