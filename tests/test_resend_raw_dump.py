"""``API_SPEND_RESEND_RAW_RESPONSE_PATH`` debug output."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from api_spend.http_raw_dump import RESEND_RAW_RESPONSE_ENV
from api_spend.providers.resend import ResendSnapshotProvider


def test_raw_dump_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    raw_path = tmp_path / "r.json"
    monkeypatch.setenv(RESEND_RAW_RESPONSE_ENV, str(raw_path))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"object": "list", "data": []},
            headers={"x-resend-monthly-quota": "1"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        ResendSnapshotProvider("re_x", client=http).read_counter()

    outer = json.loads(raw_path.read_text(encoding="utf-8"))
    assert outer["http_status"] == 200
    assert "/emails" in outer["url"]
