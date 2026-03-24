# Schemas

**Optional.** Python+Pydantic often uses this folder. Node may use root `openapi.json` or `docs/` — record in [`PLANNED_INTERFACE.md`](../PLANNED_INTERFACE.md) §0 instead.

## `public_pydantic_schemas.json`

JSON Schema keyed by model name; from public `BaseModel` + `__all__`.

| Concern | Source |
|---------|--------|
| Field meaning, env | `PLANNED_INTERFACE.md` §0, §5–§8 |
| Regen | `PUBLIC_PACKAGE` in [`scripts/export_public_schema.py`](../scripts/export_public_schema.py) then: |

```bash
cd /path/to/your-repo
python scripts/export_public_schema.py
```

**CI:** Diff against fresh export when you add a snapshot test.
