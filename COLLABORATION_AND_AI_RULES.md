# Collaboration (agents + humans)

**Product truth:** [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 + registers below.

**Agents — how much to read:** For routine coding and documentation work, read **§1–§5** only. Open **§6–§7** when editing practices in this file, doing **BACKLOG.md** / **implementation-notes.md** hygiene, or the human asks for lessons or maintenance cadence.

**Human scope:** [`README.md` — Human: scope hint](README.md#human-scope) (e.g. **Docs only**).

## 1. Agent workflow

**Precedence:** `PLANNED_INTERFACE.md` > `IMPLEMENTATION_PLAN.md` > informal code.

**Default doc pass**

1. [`README.md`](README.md) **For coding agents** + doc index.
2. If **`active-task.md`** exists (gitignored) → read **Goal** + **Status** + approved **Checklist** after human approval; **not SoT** — still update `PLANNED_INTERFACE.md` / registers per rules.
3. If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists → complete before product work → delete.
4. `PLANNED_INTERFACE.md` §0, then task sections.
5. [`TODO.md`](TODO.md) → [`DECISIONS.md`](DECISIONS.md) §2–§3 for **`Refs: D-…`**.
6. [`implementation-notes.md`](implementation-notes.md) only for history (non-normative).

**Registers**

| File | Role |
|------|------|
| `DECISIONS.md` | `D-…` §2 shipped · §3 pending · §4 open |
| `TODO.md` | Work order; **`Refs: D-…`** |
| `BACKLOG.md` | `Vx-…` + ideas; promote to interface before contract |

**Execution:** Run install/tests when toolchain exists; iterate. Trivial scope → skip **`active-task.md`** and extra approval theater.

**`active-task.md`:** Prefer checklist items that **link or mirror** [`TODO.md`](TODO.md); do not duplicate long contract text inside the task file — edit SoT files directly.

**Doc drift (same PR / change set)**

1. Public behavior / models / env → **`PLANNED_INTERFACE.md`** first.
2. **`README.md`** → only if cwd/commands/paths change; never new normative prose (§0).
3. `rg` old names in `*.md` and source.
4. Generated schema/OpenAPI → regen via **documented** command (`export_public_schema.py` + `PUBLIC_PACKAGE` **or** Node pipeline); snapshot test green if present.

**Public surface checklist**

1. `PLANNED_INTERFACE.md` — §3–§8, §8 env names; bump **Contract revision** at top when normative §§ change.
2. `README.md` — commands only if needed.
3. Exports — Python `__all__`, package `exports`, OpenAPI, etc. match contract.
4. **Static types (when stack uses them)** — **Python:** update **PEP 484** annotations for **public** APIs / models when shapes change; run **`mypy` / `pyright` / `basedpyright`** (or whatever the repo configures). **TypeScript / Node:** update shared **`.ts` types**, `d.ts`, or package **exports** the same way; run **`tsc --noEmit`** (or project check) if configured.
5. Schema artifact — regen + §0 path if committed.
6. `DECISIONS.md` / `TODO.md` — `D-…` / `Refs:` when decision-gated.

**Post-change:** Repo root; env per README (venv / lockfile install); full tests; `rg` renames; add CI when code lands.

**Code style:** Minimal diff; match file; reuse helpers.

**Explanations:** Code citations `startLine:endLine:path`; use thread for intent.

## 2. Cursor rules

| File | Role |
|------|------|
| [`.cursorrules`](.cursor/rules/.cursorrules) | Plan vs implement; small functions; evidence when debugging |
| [`implementation-decisions.mdc`](.cursor/rules/implementation-decisions.mdc) | TODO/DECISIONS; interface before code; `Vx-…` |
| [`markdown-agent-priority.mdc`](.cursor/rules/markdown-agent-priority.mdc) | Edit `*.md`: SoT, tables, links, terminal blocks |

New repo: copy `.cursor/rules/`; fix paths; adjust `globs` / `alwaysApply`.

## 3. Global user rules (optional)

Run commands; fix failures; markdown links for web; repo paths in code fences; never echo secrets.

## 4. Bootstrap vs interface planning

| Phase | Do |
|-------|-----|
| **`BOOTSTRAP.md` present** | Run end-to-end: tooling + README commands + `PLANNED_INTERFACE.md` §0 machinery only. Delete file; `rg BOOTSTRAP.md`. |
| **After removal** | README + `IMPLEMENTATION_PLAN.md` §2 only. |
| **Interface planning** | Human drives `PLANNED_INTERFACE.md` §1+ → then `DECISIONS` / `TODO` / `BACKLOG` / tests / `.env.example`. |
| **Active task** | Optional: [`active-task.template.md`](active-task.template.md) → **`active-task.md`** (gitignored). Human deletes **`active-task.md`** when task completes. |

## 5. Template rename pass

Replace **Your Project** / org / package strings. Grow `PLANNED_INTERFACE.md` before real `TODO` phases. One `D-…` per fork in `DECISIONS.md`.

## 6. Lessons

Prune stale bullets; promote durable ones here from `implementation-notes.md`.

- Names: contract ≡ code ≡ tests ≡ schema fields.
- Before deleting fixtures: `rg` paths; run tests.
- Examples in contract = shipped shape; futures → `BACKLOG.md`.
- Committed schema: regen script + snapshot test.
- Live tests: off by default + env flag; document in README.
- Python: `python3 -m venv .venv`; `.venv/` gitignored; PEP 668.
- Node: lockfile + Node version (`.nvmrc` / `engines` / Volta); `node_modules/` gitignored.
- Validation errors → documented public error types at boundaries.
- Python logging: named loggers under package; app sets handlers; no secrets.
- Node logging: structured + redact secrets.

## 7. Maintain

**§6:** Update when practices change. **§1–§5:** Match docs you actually use. **Agents:** see **How much to read** at top — skip §6–§7 unless hygiene or explicit ask.

**`BACKLOG.md`:** Quarterly or per release — ship folded items; short `Vx-…`; open bullets must not duplicate contract.

**`implementation-notes.md`:** On release or touched code — prune; promote to §6 first.
