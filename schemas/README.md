# Schemas

## `public_pydantic_schemas.json`

Machine-readable **JSON Schema** for each public **`BaseModel`** re-exported from **`api_spend`** (derived from `api_spend.__all__` via `model_json_schema()`).

- **Semantics** (field meaning, coverage rules, env names): [`PLANNED_INTERFACE.md`](../PLANNED_INTERFACE.md) §5–§6 and §8 (**§0** SoT).
- **Regenerate** after changing those models:

  ```bash
  cd /path/to/api-spend
  python scripts/export_public_schema.py
  pytest -q tests/test_public_schema_snapshot.py
  ```

- **CI:** [`tests/test_public_schema_snapshot.py`](../tests/test_public_schema_snapshot.py) diffs this file to a fresh export.
