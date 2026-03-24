#!/usr/bin/env python3
"""Write schemas/public_pydantic_schemas.json from a package's public BaseModels.

Template: set PUBLIC_PACKAGE to your top-level import name (must expose __all__ with
BaseModel subclasses). Leave as None until the package exists; the script then writes
an empty object and exits 0 (no third-party deps required).
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

# e.g. "my_package" after `src/my_package` exists and is on PYTHONPATH / installed.
PUBLIC_PACKAGE: str | None = None

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "schemas" / "public_pydantic_schemas.json"


def main() -> None:
    if not PUBLIC_PACKAGE:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("{}\n", encoding="utf-8")
        print(
            "Wrote empty schemas/public_pydantic_schemas.json — set PUBLIC_PACKAGE in "
            "scripts/export_public_schema.py when your package is ready.",
            file=sys.stderr,
        )
        return

    from pydantic import BaseModel

    mod = importlib.import_module(PUBLIC_PACKAGE)
    names = sorted(getattr(mod, "__all__", ()))
    out: dict = {}
    for name in names:
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
            out[name] = obj.model_json_schema()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(out)} models)")


if __name__ == "__main__":
    main()
