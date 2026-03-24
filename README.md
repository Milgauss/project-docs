# Project documentation template

Contract-first markdown + Cursor rules. Replace placeholders as you adopt.

**Agent precedence:** `PLANNED_INTERFACE.md` > `IMPLEMENTATION_PLAN.md` > code. Commands live in this file, not duplicate contract prose ([§0 SoT](PLANNED_INTERFACE.md#sources-of-truth)).

**Optional:** [`schemas/`](schemas/) + [`scripts/export_public_schema.py`](scripts/export_public_schema.py) (Python / Pydantic JSON Schema). Node/OpenAPI: record path + regen in `PLANNED_INTERFACE.md` §0.

**`BOOTSTRAP.md`:** If the file exists → run once (tooling + README commands + `PLANNED_INTERFACE.md` §0 rows only; no §1–§7 design) → delete per that file. If absent → skip.

---

<a id="for-coding-agents"></a>

## For coding agents

| Step | Action |
|------|--------|
| **Entry** | This section + **Documentation index** below. |
| **Active task** | If **`active-task.md`** exists (local, gitignored) → read **Goal** + **Status**. Not SoT. If `awaiting_human_approval` → propose doc deltas + checklist; stop for human. If `approved` → execute checklist; human deletes file when done. Skip for trivial work. |
| **Bootstrap** | If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists → complete it, then delete it. Else skip. |
| **SoT** | [`PLANNED_INTERFACE.md` §0](PLANNED_INTERFACE.md#sources-of-truth) — who owns each fact type. |
| **Read order** | `PLANNED_INTERFACE.md` → `IMPLEMENTATION_PLAN.md` → [`TODO.md`](TODO.md) → [`DECISIONS.md`](DECISIONS.md) §2–§3 when `TODO` has `Refs: D-…` → optional [`BACKLOG.md`](BACKLOG.md), [`implementation-notes.md`](implementation-notes.md). |
| **Public API edits** | [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §1 checklist + post-change ritual. |

<a id="cold-start"></a>

### Cold start (default path)

If no local **`active-task.md`** and no pending **[`BOOTSTRAP.md`](BOOTSTRAP.md)** work, open **in order** (then add code paths the task needs):

1. [`README.md`](README.md#for-coding-agents) — this section + [Documentation index](#documentation-index)
2. [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md#sources-of-truth) — §0 SoT, then task §§
3. [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) — §2–§4
4. [`TODO.md`](TODO.md)
5. [`DECISIONS.md`](DECISIONS.md) — when `TODO.md` has **`Refs: D-…`**
6. [`BACKLOG.md`](BACKLOG.md) — when task is v2+ / backlog
7. [`implementation-notes.md`](implementation-notes.md) — only for history / debugging

<a id="human-scope"></a>

### Human: scope hint (use every turn when helpful)

Lead with a **narrow scope** so agents skip unrelated trees. Examples:

- **`Docs only`** or **`documentation only`** — markdown / contract registers only; do not read app source except to verify a cited path or example.
- **`Touches:`** `src/foo.ts`, `tests/bar.test.ts` — prefer those paths + SoT docs; avoid broad repo search.

Agents: honor the hint. **Docs-only** still uses **`PLANNED_INTERFACE.md`** / **`DECISIONS.md`** / **`TODO.md`** when editing behavior — do not invent new normative rules in **`README.md`** ([§0](PLANNED_INTERFACE.md#sources-of-truth)).

<a id="task-first-open"></a>

### Task → open first

| If the task is … | Open first (then usual read order) |
|------------------|--------------------------------------|
| New repo / stack / `cd`+install | [`BOOTSTRAP.md`](BOOTSTRAP.md) if present; else [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2 + this README |
| Env var names / required / purpose | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §8 (and §0) |
| Public types / schema / OpenAPI path | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 → artifact path; regen per §0 / [`schemas/README.md`](schemas/README.md) |
| What to build next / checkpoints | [`TODO.md`](TODO.md) → [`DECISIONS.md`](DECISIONS.md) if `Refs: D-…` |
| Future / v2+ idea (not contract) | [`BACKLOG.md`](BACKLOG.md) |
| Integration with parent system | [`SYSTEM_CONTEXT.md`](SYSTEM_CONTEXT.md) (optional; contract wins) |
| Pick or add a **library** | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2, then [`FRAMEWORKS.md`](FRAMEWORKS.md) |
| Complex multi-step task (context handoff) | **`active-task.md`** if present ([`active-task.template.md`](active-task.template.md) → copy); else usual read order |
| **Docs only** / **documentation only** (human said so) | [Cold start](#cold-start) docs only: `README.md` → `PLANNED_INTERFACE.md` (§0 + sections being edited) → `COLLABORATION_AND_AI_RULES.md` §1 (drift/checklists) → `TODO` / `DECISIONS` / `BACKLOG` as touched. **Skip** [`FRAMEWORKS.md`](FRAMEWORKS.md); **skip** source trees unless verifying a link. |

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
| [`BOOTSTRAP.md`](BOOTSTRAP.md) | If present: run then remove. Not product design. |
| [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) | Contract; §0 SoT; §1+ when human drives design |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Stack §2, layout §3, phases §4 |
| [`TODO.md`](TODO.md) | `[ ]` / `[x]` only; `Refs: D-…` |
| [`DECISIONS.md`](DECISIONS.md) | `D-…` §2 shipped / §3 pending |
| [`BACKLOG.md`](BACKLOG.md) | `Vx-…`; not contract until merged into interface |
| [`implementation-notes.md`](implementation-notes.md) | Retros; non-normative |
| [`SYSTEM_CONTEXT.md`](SYSTEM_CONTEXT.md) | Optional integration context; contract wins on conflict |
| [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) | Process, drift, lessons |
| [`CHANGELOG.md`](CHANGELOG.md) | Releases |
| [`schemas/public_pydantic_schemas.json`](schemas/public_pydantic_schemas.json) | Optional; Python/Pydantic path |
| [`scripts/export_public_schema.py`](scripts/export_public_schema.py) | Pydantic export; set `PUBLIC_PACKAGE` |
| [`FRAMEWORKS.md`](FRAMEWORKS.md) | **Skip** unless adding/choosing a dependency; not SoT |
| [`AGENTS.md`](AGENTS.md) | Thin entry pointer for tools; links here |
| [`active-task.template.md`](active-task.template.md) | Copy → **`active-task.md`** (gitignored) for complex tasks; delete `active-task.md` when done |

**Human-only** ([`.cursorignore`](.cursorignore)): [`ai-prompt-examples.md`](ai-prompt-examples.md) — not SoT; omit from default doc pass.

<a id="rg-registers"></a>

### `rg` — registers (optional)

```bash
rg 'Refs:' TODO.md
rg 'D-[A-Za-z0-9-]+' DECISIONS.md
rg 'V[0-9]+-[A-Za-z0-9-]+' BACKLOG.md
rg 'Vx-' BACKLOG.md
```

Adjust patterns if your `D-…` / `Vx-…` naming differs.

---

## First-time (template → real repo)

1. Replace **Your Project** / org strings repo-wide; set [`LICENSE`](LICENSE) copyright if you fork this template.
2. If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists: agent runs it with human → delete file → grep `BOOTSTRAP.md` and fix links.
3. Interface design: human prompts content into `PLANNED_INTERFACE.md` §1+; then `TODO` / `DECISIONS` / `BACKLOG` as usual.
4. Add `pyproject.toml` and/or `package.json` (+ lockfiles), CI; keep **cd/install/test** here accurate.

**Complex tasks (optional):** copy [`active-task.template.md`](active-task.template.md) to **`active-task.md`**, fill goal, run the approve → execute loop in that file; delete **`active-task.md`** when finished.

---

## License

[`LICENSE`](LICENSE)
