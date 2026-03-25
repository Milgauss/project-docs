# Collaboration (agents + humans)

**Product truth:** [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 + registers below.

**Agents — how much to read:** For routine coding and documentation work, read **§1–§5** only. Open **§6–§7** when editing practices in this file, doing **BACKLOG.md** / **implementation-notes.md** hygiene, or the human asks for lessons or maintenance cadence.

**Human scope:** [`README.md` — Human: scope hint](README.md#human-scope) (e.g. **Docs only**).

## 1. Agent workflow

See [`.cursor/rules/agent-workflow.mdc`](.cursor/rules/agent-workflow.mdc) for the primary workflow.

**Doc drift (same PR / change set)**

1. Public behavior / models / env → **`PLANNED_INTERFACE.md`** first.
2. **`README.md`** → only if cwd/commands/paths change; never new normative prose (per `PLANNED_INTERFACE.md` §0).
3. `rg` old names in `*.md` and source.
4. Generated schema/OpenAPI → regen via **documented** command (`export_public_schema.py` + `PUBLIC_PACKAGE` **or** Node pipeline); snapshot test green if present.

**Public surface checklist**

See [`.cursor/rules/agent-workflow.mdc`](.cursor/rules/agent-workflow.mdc) for the public surface checklist.

**Post-change:** Repo root; env per README (venv / lockfile install); full tests; `rg` renames; add CI when code lands.

**Code style:** Minimal diff; match file; reuse helpers.

**Explanations:** Code citations `startLine:endLine:path`; use thread for intent.

## 2. Cursor rules

| File | Role |
|------|------|
| [`agent-workflow.mdc`](.cursor/rules/agent-workflow.mdc) | Default doc pass, execution, doc drift |
| [`implementation-decisions.mdc`](.cursor/rules/implementation-decisions.mdc) | PLAN/DECISIONS; interface before code; `Vx-…` |
| [`markdown-agent-priority.mdc`](.cursor/rules/markdown-agent-priority.mdc) | Edit `*.md`: SoT, tables, links, terminal blocks |

New repo: copy `.cursor/rules/`; fix paths; adjust `globs` / `alwaysApply`.

## 3. Global user rules (optional)

Run commands; fix failures; markdown links for web; repo paths in code fences; never echo secrets.

## 4. Bootstrap vs interface planning

| Phase | Do |
|-------|-----|
| **`BOOTSTRAP.md` present** | Run end-to-end: tooling + README commands + `PLANNED_INTERFACE.md` §0 machinery only. Rename file to `INIT_LOG.md`; `rg BOOTSTRAP.md`. |
| **After removal/rename** | README + `PLAN.md` §2 only. |
| **Interface planning** | Human drives `PLANNED_INTERFACE.md` §1+ → then `DECISIONS.md` / `PLAN.md` / `BACKLOG.md` / tests / `.env.example`. |
| **Active task** | Optional: [`active-task.template.md`](active-task.template.md) → **`active-task.md`** (gitignored). Human deletes **`active-task.md`** when task completes. |

## 5. Template rename pass

Replace **Your Project** / org / package strings. Grow `PLANNED_INTERFACE.md` before real `PLAN.md` checklists. One `D-…` per fork in `DECISIONS.md`.

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
