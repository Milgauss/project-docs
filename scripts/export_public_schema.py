#!/usr/bin/env python3
"""Write schemas/public_pydantic_schemas.json from api_spend public BaseModels."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[1]
_src = str(REPO / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import api_spend  # noqa: E402


def main() -> None:
    out: dict = {}
    for name in sorted(api_spend.__all__):
        obj = getattr(api_spend, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
            out[name] = obj.model_json_schema()
    path = REPO / "schemas" / "public_pydantic_schemas.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {path} ({len(out)} models)")


if __name__ == "__main__":
    main()
