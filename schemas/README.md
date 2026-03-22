# Schemas (optional)

If **`PLANNED_INTERFACE.md`** defines JSON (or similar) output:

1. Add a **JSON Schema** file here (e.g. `result.json`) for integrators and agents.
2. Document regeneration in **`PLANNED_INTERFACE.md`** or **`README.md`** (e.g. a small script under `scripts/` that exports from your models).
3. Add a **test** that fails if the committed file drifts from the live export.

No schema is required for the methodology to work—only when machine validation adds value.
