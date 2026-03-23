"""Opt-in HTTP response capture for provider adapters (see README *Raw API responses*)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

OPENAI_RAW_RESPONSE_ENV = "API_SPEND_OPENAI_RAW_RESPONSE_PATH"
ANTHROPIC_RAW_RESPONSE_ENV = "API_SPEND_ANTHROPIC_RAW_RESPONSE_PATH"
BRIGHTDATA_RAW_RESPONSE_ENV = "API_SPEND_BRIGHTDATA_RAW_RESPONSE_PATH"
RESEND_RAW_RESPONSE_ENV = "API_SPEND_RESEND_RAW_RESPONSE_PATH"
BRAVE_RAW_RESPONSE_ENV = "API_SPEND_BRAVE_RAW_RESPONSE_PATH"


def maybe_dump_http_response(response: httpx.Response, env_var_name: str) -> None:
    """If ``env_var_name`` is set, append or print a JSON envelope for this response.

    Value: file path, or ``-`` / ``stdout`` / ``stderr``. File targets append ``---``
    between consecutive responses in the same run.
    """
    target = os.environ.get(env_var_name, "").strip()
    if not target:
        return

    text = response.text or ""
    envelope: dict[str, Any] = {
        "http_status": response.status_code,
        "url": str(response.request.url),
    }
    try:
        envelope["json"] = json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        envelope["text"] = text

    out = json.dumps(envelope, indent=2) + "\n"
    if target in ("-", "stdout"):
        sys.stdout.write(out)
        return
    if target == "stderr":
        sys.stderr.write(out)
        return

    path = Path(target).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        prev = path.read_text(encoding="utf-8")
        path.write_text(prev + "\n---\n" + out, encoding="utf-8")
    else:
        path.write_text(out, encoding="utf-8")
