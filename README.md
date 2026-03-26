# Project documentation template

Contract-first markdown + Cursor rules. Replace placeholders as you adopt.

**Agent precedence:** `PLANNED_INTERFACE.md` > `PLAN.md` > code. Commands live in this file, not duplicate contract prose ([§0 SoT](PLANNED_INTERFACE.md#sources-of-truth)).

**Optional:** [`schemas/`](schemas/) + [`scripts/export_public_schema.py`](scripts/export_public_schema.py) (Python / Pydantic JSON Schema). Node/OpenAPI: record path + regen in `PLANNED_INTERFACE.md` §0.

**`BOOTSTRAP.md`:** If the file exists → run once (tooling + README commands + `PLANNED_INTERFACE.md` §0 rows only; no §1–§7 design) → rename to `INIT_LOG.md` per that file. If absent → skip.

---

<a id="for-coding-agents"></a>

## For coding agents

| Step | Action |
|------|--------|
| **Entry** | This section + **Documentation index** below. |
| **Active task** | Use **Taskmaster MCP** for granular execution tracking of complex tasks. Do not use local markdown files for micro-steps. |
| **Bootstrap** | If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists → complete it, then rename to `INIT_LOG.md`. Else skip. |
| **SoT** | [`PLANNED_INTERFACE.md` §0](PLANNED_INTERFACE.md#sources-of-truth) — who owns each fact type. |
| **Read order** | `PLANNED_INTERFACE.md` → `PLAN.md` → [`DECISIONS.md`](DECISIONS.md) §2–§3 when `PLAN.md` has `Refs: D-…` → optional [`BACKLOG.md`](BACKLOG.md), [`implementation-notes.md`](implementation-notes.md). |
| **Public API edits** | [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §1 checklist + post-change ritual. |

<a id="cold-start"></a>

### Cold start (default path)

If no pending **[`BOOTSTRAP.md`](BOOTSTRAP.md)** work, open **in order** (then add code paths the task needs):

1. [`README.md`](README.md#for-coding-agents) — this section + [Documentation index](#documentation-index)
2. [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md#sources-of-truth) — §0 SoT, then task §§
3. [`PLAN.md`](PLAN.md) — §2–§4
4. [`DECISIONS.md`](DECISIONS.md) — when `PLAN.md` has **`Refs: D-…`**
5. [`BACKLOG.md`](BACKLOG.md) — when task is v2+ / backlog
6. [`implementation-notes.md`](implementation-notes.md) — only for history / debugging

<a id="human-scope"></a>

### Human: scope hint (use every turn when helpful)

Lead with a **narrow scope** so agents skip unrelated trees. Examples:

- **`Docs only`** or **`documentation only`** — markdown / contract registers only; do not read app source except to verify a cited path or example.
- **`Touches:`** `src/foo.ts`, `tests/bar.test.ts` — prefer those paths + SoT docs; avoid broad repo search.

Agents: honor the hint. **Docs-only** still uses **`PLANNED_INTERFACE.md`** / **`DECISIONS.md`** / **`PLAN.md`** when editing behavior — do not invent new normative rules in **`README.md`** ([§0](PLANNED_INTERFACE.md#sources-of-truth)).

<a id="task-first-open"></a>

### Task → open first

| If the task is … | Open first (then usual read order) |
|------------------|--------------------------------------|
| New repo / stack / `cd`+install | [`BOOTSTRAP.md`](BOOTSTRAP.md) if present; else [`PLAN.md`](PLAN.md) §2 + this README |
| Env var names / required / purpose | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §8 (and §0) |
| Public types / schema / OpenAPI path | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 → artifact path; regen per §0 / [`schemas/README.md`](schemas/README.md) |
| What to build next / checkpoints | [`PLAN.md`](PLAN.md) (Checklists) → [`DECISIONS.md`](DECISIONS.md) if `Refs: D-…` |
| Future / v2+ idea (not contract) | [`BACKLOG.md`](BACKLOG.md) |
| Integration with parent system | [`SYSTEM_CONTEXT.md`](SYSTEM_CONTEXT.md) (optional; contract wins) |
| Complex multi-step task (context handoff) | Check **Taskmaster MCP** for current state; else usual read order |
| **Docs only** / **documentation only** (human said so) | [Cold start](#cold-start) docs only: `README.md` → `PLANNED_INTERFACE.md` (§0 + sections being edited) → `COLLABORATION_AND_AI_RULES.md` §1 (drift/checklists) → `PLAN.md` / `DECISIONS.md` / `BACKLOG.md` as touched. **Skip** source trees unless verifying a link. |

**Required when a test runner exists:** Fenced **cd**, **install**, **test** blocks here (real paths/commands). Until then, placeholder:

```bash
# cd /path/to/this/repo
# install: …
# test: …
```

---

## Documentation index

| Path | Agent use |
|------|-----------|
| [`BOOTSTRAP.md`](BOOTSTRAP.md) | If present: run then rename to `INIT_LOG.md`. Not product design. |
| [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) | Contract; §0 SoT; §1+ when human drives design |
| [`PLAN.md`](PLAN.md) | Stack §2, layout §3, phase checklists §4 |
| [`DECISIONS.md`](DECISIONS.md) | `D-…` §2 shipped / §3 pending |
| [`BACKLOG.md`](BACKLOG.md) | `Vx-…`; not contract until merged into interface |
| [`implementation-notes.md`](implementation-notes.md) | Retros; non-normative |
| [`SYSTEM_CONTEXT.md`](SYSTEM_CONTEXT.md) | Optional integration context; contract wins on conflict |
| [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) | Process, drift, lessons |
| [`CHANGELOG.md`](CHANGELOG.md) | Releases |
| [`schemas/public_pydantic_schemas.json`](schemas/public_pydantic_schemas.json) | Optional; Python/Pydantic path |
| [`scripts/export_public_schema.py`](scripts/export_public_schema.py) | Pydantic export; set `PUBLIC_PACKAGE` |
| [`AGENTS.md`](AGENTS.md) | Thin entry pointer for tools; links here |
| [`active-task.template.md`](active-task.template.md) | **DEPRECATED:** Use Taskmaster MCP instead. |

**Human-only** ([`.cursorignore`](.cursorignore)): `_human-docs/` (e.g. `INITIAL_REQUIREMENTS.md`, `ai-prompt-examples.md`) — not SoT; omit from default doc pass.

<a id="rg-registers"></a>

### `rg` — registers (optional)

```bash
rg 'Refs:' PLAN.md
rg 'D-[A-Za-z0-9-]+' DECISIONS.md
rg 'V[0-9]+-[A-Za-z0-9-]+' BACKLOG.md
rg 'Vx-' BACKLOG.md
```

Adjust patterns if your `D-…` / `Vx-…` naming differs.

---

## First-time (template → real repo)

1. Replace **Your Project** / org strings repo-wide; set [`LICENSE`](LICENSE) copyright if you fork this template.
2. If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists: agent runs it with human → rename file to `INIT_LOG.md` → grep `BOOTSTRAP.md` and fix links.
3. Interface design: human prompts content into `PLANNED_INTERFACE.md` §1+; then `PLAN.md` / `DECISIONS.md` / `BACKLOG.md` as usual.
4. Add `pyproject.toml` and/or `package.json` (+ lockfiles), CI; keep **cd/install/test** here accurate.

**Complex tasks (optional):** use **Taskmaster MCP** to generate a structured task graph and execute micro-steps iteratively.

---

## License

[`LICENSE`](LICENSE)
