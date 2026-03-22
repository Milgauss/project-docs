# Collaboration: human + AI

How we work—reusable as a **template** for other projects. Product truth lives in `**PLANNED_INTERFACE.md`** and related registers; this file is **process and tooling**.

---

## 1. Process

**Truth order:** `**PLANNED_INTERFACE.md`** wins over `**IMPLEMENTATION_PLAN.md**` or code guesses.

**Registers:**


| Doc                | Role                                                                                                                                                                                                                                                                               |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**DECISIONS.md`** | v1 `**D-…**`: **§2** shipped, **§3** pending, **§4** open forks.                                                                                                                                                                                                                   |
| `**TODO.md`**      | Ordered v1 checklist; `**Refs: D-…**` where a row exists.                                                                                                                                                                                                                          |
| `**BACKLOG.md**`   | `**Vx-…**` (pre-interface) + backlog for **v2, v3+, or unversioned** work. Promote to `**PLANNED_INTERFACE.md`** before treating as contract; optional `**TODO_V2.md**`, … + `**Refs: V2-…**`. Future-version work is **not** a `**D-…`** unless you deliberately fold it into v1. |


**Execution (AI):** Run the environment—install, tests, diagnose. Do not stop at the first failure; fix or narrow, then report. Well-scoped tasks can ship without step-by-step approval.

**Code:** Minimal diffs; match local style; reuse helpers instead of parallel implementations.

**Explanations:** Prefer **code citations** (`startLine:endLine:path`) for existing code; clear prose; read the **thread** for intent (refinement vs new ask).

---

## 2. Cursor rules (this workspace)

Under `**.cursor/rules/`**:


| File                                                                         | Purpose                                                                                                                                                          |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[.cursorrules](.cursor/rules/.cursorrules)`                                 | Complex work → short plan + approval; simple → go; small functions; debug with evidence/logging before guessing.                                                 |
| `[implementation-decisions.mdc](.cursor/rules/implementation-decisions.mdc)` | Before coding: v1 ↔ `**TODO`/`DECISIONS**`; work without `**D-…**` ↔ `**BACKLOG.md**` + interface; locked future work ↔ `**Vx-…**` then `**PLANNED_INTERFACE**`. |


**New repo:** Copy `**.cursor/rules/`**, retarget doc paths if needed, adjust `**globs**` / `**alwaysApply**` in `**.mdc**` files.

---

## 3. User-level rules (optional)

Often set as **global Cursor user rules**. Themes: run commands and fix issues yourself; **markdown links** for web refs; **code blocks** for repo code; never log or echo **secrets**.

---

## 4. Bootstrap checklist (new project)

1. One **contract** doc (surface area, formats, errors, exit codes).
2. `**DECISIONS.md`** + `**TODO.md**` with `**Refs: D-…**` where decisions exist.
3. `**BACKLOG.md**` with `**Vx-…**` register + ideas for **v2+**.
4. **Cursor rules** pointing at those docs.
5. **Tests** the agent can run; **README** + `**.env.example`** if you use env-gated features; a **validate** command or equivalent if configuration must be checked before execution.

---

## 5. Applying this template to your repo

Names in this repo: CLI **`api-spend`**, Python package path **`api_spend`**, product title **API Spend** — keep them aligned across docs and packaging. Do not begin editing **`PLANNED_INTERFACE.md`** until instructed by the human. Fill **`PLANNED_INTERFACE.md`** before expanding **`TODO.md`** into a long checklist. Keep **`DECISIONS.md`** sparse: one row per real fork, not per task.

---

## 6. Lessons learned

Short, actionable; prune when stale. Append when something pays off or burns you; copy or trim when starting a sibling project.

- **Vocabulary:** Match the contract and schema field names in code, tests, and docs.
- **Scratch artifacts:** Before deleting generated files or fixtures, `**grep`** the repo for paths; run tests after cleanup.
- **Samples:** Examples in `**PLANNED_INTERFACE.md`** should match **what is shipped**; future-only fields belong in `**BACKLOG.md`** or clearly marked draft sections.
- **CLI help vs README:** Operator-facing limits should match `**--help`**, README, and tests if you lock help text with assertions.
- **JSON Schema:** If you export schema from models, commit the file and add a test that compares export to committed artifact so refactors cannot drift silently.
- **Integration tests:** Live dependencies **skipped by default**; document the env flag; keep default test runs fast.

---

## 7. Maintaining this file

Update **§6** when team practices evolve; keep **§1–§5** aligned with the doc set you actually use.