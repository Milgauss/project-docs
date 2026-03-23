"""Opt-in full-stack live test for ``ApiSpend`` (``TODO.md`` Phase 8.2, ``README.md``).

Optional JSON artifact (same env var as other live tests)::

    export API_SPEND_LIVE_DUMP_PATH=./api_spend_full_stack_live.json

Writes ``validate``, ``sync``, ``query``, ``status``, and ``providers`` (Pydantic
``model_dump(mode='json')``) after a successful run.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path

import pytest

from api_spend import ApiSpend
from api_spend.config import PROVIDER_CREDENTIAL_ENV, load_config
from api_spend.store import SpendStore

pytestmark = pytest.mark.skipif(
    os.environ.get("API_SPEND_LIVE_TESTS") != "1",
    reason="set API_SPEND_LIVE_TESTS=1 to run (see README)",
)


def test_api_spend_validate_sync_query_live(tmp_path: Path) -> None:
    cfg_path = os.environ.get("API_SPEND_CONFIG", "").strip()
    if not cfg_path:
        pytest.skip("API_SPEND_CONFIG must point at a YAML file (see README)")
    cfg_file = Path(cfg_path).expanduser()
    if not cfg_file.is_file():
        pytest.skip(f"API_SPEND_CONFIG not found: {cfg_file}")

    app_cfg, _ = load_config(cfg_file, require_credentials=False)
    if not app_cfg.providers:
        pytest.skip("config has no providers")

    missing = [
        p.name
        for p in app_cfg.providers
        if not os.environ.get(PROVIDER_CREDENTIAL_ENV[p.name], "").strip()
    ]
    if missing:
        pytest.skip(f"missing API keys for providers: {sorted(missing)}")

    db = tmp_path / "api_spend_live.sqlite"
    store = SpendStore.open(db)
    client = ApiSpend(str(cfg_file), store=store, require_credentials=True)
    try:
        vr = client.validate(check_connectivity=False)
        bad = [r for r in vr.providers if not r.config_ok or not r.credentials_ok]
        if bad:
            pytest.skip(f"validate preflight failed: {bad!r}")

        sr = client.sync()
        if not any(s.ok for s in sr.providers):
            pytest.fail(f"all providers failed sync: {sr!r}")

        end = date.today()
        start = end - timedelta(days=400)
        qr = client.query(start, end, granularity="month")
        assert qr.buckets is not None

        dump_path = os.environ.get("API_SPEND_LIVE_DUMP_PATH", "").strip()
        if dump_path:
            out = Path(dump_path).expanduser().resolve()
            payload = {
                "validate": vr.model_dump(mode="json"),
                "sync": sr.model_dump(mode="json"),
                "query": qr.model_dump(mode="json"),
                "status": client.status().model_dump(mode="json"),
                "providers": [p.model_dump(mode="json") for p in client.providers()],
            }
            out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    finally:
        client.close()
        store.close()
