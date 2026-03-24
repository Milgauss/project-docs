# Bootstrap (delete when done)

**Agent + human.** One-time: align **tooling**, **README copy-paste commands**, and **`PLANNED_INTERFACE.md` §0** (schema/OpenAPI *paths and regen only*).

**Do not:** fill `PLANNED_INTERFACE.md` §1–§7, add product **`D-…`**, or expand `TODO`/`BACKLOG` with design — unless the human explicitly switches to interface planning in the same thread.

**While this file exists:** `README.md` **For coding agents** is the permanent home for commands; this file is the questionnaire + checklist.

---

## Ask the human (skip N/A)

1. Languages: Python, Node, or both?
2. Python: version? layout (`src/` …) when code exists? package name can stay TBD.
3. Node: version or defer (`.nvmrc` / `engines`)? npm / pnpm / yarn?
4. Repo root: same dir as future `pyproject.toml` / `package.json`, or docs-only path? (sets **cd** in README)
5. Default test command (`pytest`, `pnpm test`, …) even if smoke-only.
6. Committed machine-readable public surface: Pydantic JSON Schema, OpenAPI, Zod→JSON Schema, or **none yet**? (§0 records path + regen only.)
7. CI now or defer?

---

## Agent edits (framework only)

| # | Target | Action |
|---|--------|--------|
| 1 | `IMPLEMENTATION_PLAN.md` §2 | Fill stack table from answers. |
| 2 | `README.md` | Fenced **cd**, **install**, **test** under **For coding agents**. |
| 3 | `PLANNED_INTERFACE.md` §0 | Update optional-schema row; no dead paths; honest **none yet**. |
| 4 | Optional | Human wants minimal tree + no Pydantic → remove unused `schemas/`, `scripts/export_public_schema.py`; fix §0. |
| 5 | Optional | `.nvmrc`, `engines`, `.gitignore` per human. |
| 6 | Optional | Minimal CI + mention in README if human asked. |

---

## Done when

- [ ] `IMPLEMENTATION_PLAN.md` §2 not all placeholder.
- [ ] `README.md` has working **cd / install / test**.
- [ ] `PLANNED_INTERFACE.md` §0 matches real artifacts or states none/TBD.
- [ ] Human confirms.

**Then:** Delete this file; `rg BOOTSTRAP.md`; drop README index row; optional note in `CHANGELOG.md` / `implementation-notes.md`.

**Next:** Interface planning → `PLANNED_INTERFACE.md` §1+ → `TODO` / `DECISIONS` / `BACKLOG`.
