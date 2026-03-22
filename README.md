# API Spend

Track API usage and spend (scope and audience to be refined with the contract in `PLANNED_INTERFACE.md`).

**Status:** **v1** — (one line: what is shipped vs in progress). **`D-…`** register: [`DECISIONS.md`](DECISIONS.md). **Future work (v2+):** [`BACKLOG.md`](BACKLOG.md) — **`Vx-…`** locked decisions + open ideas until merged into [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md).

---

## Documentation (read in this order)

| Doc | Purpose |
| --- | --- |
| [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) | **Contract:** public interface (flags, formats, exit codes, error shape, config semantics). |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | **How we build it:** phases, module layout, stack summary. |
| [`DECISIONS.md`](DECISIONS.md) | **v1 register:** **§2** shipped **`D-…`**, §3 locked pending code, §4 open forks; [`TODO.md`](TODO.md) **`Refs:`**. |
| [`TODO.md`](TODO.md) | **v1 checklist:** implement → test. |
| [`BACKLOG.md`](BACKLOG.md) | **`Vx-…`** register + backlog for **v2+**; **not** contract until merged into **`PLANNED_INTERFACE.md`**. |
| [`schemas/`](schemas/) | Optional **JSON Schema** (or other machine-readable contracts) checked into the repo; add export/regeneration notes here or in the interface doc. |
| [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) | **Human + AI workflow:** Cursor rules, collaboration checklist. |
| [`FRAMEWORKS.md`](FRAMEWORKS.md) | Tooling catalog; preferred defaults in [`.cursor/rules/.cursorrules`](.cursor/rules/.cursorrules). |

If anything disagrees, **[`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md)** wins.

---

## Stack

Summarize runtime and dev dependencies (or point to `pyproject.toml`, `package.json`, etc.). Keep secrets and env var **names** documented here and in **`PLANNED_INTERFACE.md`** — never example values.

---

## Install & usage

```bash
# Example only — replace with your project’s commands
api-spend --help
```

---

## License

*Add a `LICENSE` file when you publish.*
