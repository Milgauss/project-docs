"""``API_SPEND_BRAVE_RAW_RESPONSE_PATH`` debug output."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from api_spend.http_raw_dump import BRAVE_RAW_RESPONSE_ENV
from api_spend.providers.brave import BraveSnapshotProvider


def test_raw_dump_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "b.json"
    monkeypatch.setenv(BRAVE_RAW_RESPONSE_ENV, str(raw_path))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={},
            headers={"X-RateLimit-Limit": "10", "X-RateLimit-Remaining": "9"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        BraveSnapshotProvider("BSA_x", client=http).read_counter()

    outer = json.loads(raw_path.read_text(encoding="utf-8"))
    assert outer["http_status"] == 200
    assert "web/search" in outer["url"]
