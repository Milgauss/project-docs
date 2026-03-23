"""Snapshot of JSON schemas for public Pydantic models (api_spend.__all__)."""

from __future__ import annotations

import json
from pathlib import Path

import api_spend
from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "schemas" / "public_pydantic_schemas.json"


def _current_schemas() -> dict:
    out: dict = {}
    for name in sorted(api_spend.__all__):
        obj = getattr(api_spend, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
            out[name] = obj.model_json_schema()
    return out


def test_public_pydantic_schemas_match_snapshot() -> None:
    current = _current_schemas()
    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert current == expected, (
        "Public model JSON schemas drifted from schemas/public_pydantic_schemas.json. "
        "If intentional, regenerate: `python scripts/export_public_schema.py` from repo root."
    )
