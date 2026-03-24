# Active task — copy to `active-task.md`

**Human:** `cp active-task.template.md active-task.md` (or create `active-task.md` with this structure). **`active-task.md` is gitignored** — not committed.

**Not SoT.** Product truth stays in [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 and registers. This file is **mission + agreed steps** for **complex** work only; skip for trivial edits.

**When done:** delete `active-task.md` (human).

---

## Workflow

| # | Who | Action |
|---|-----|--------|
| 1 | Human | Fill **Goal**, set **Status** → `draft`. |
| 2 | AI | Propose **Doc / contract updates** (what changes, where) + **Checklist**; link [`TODO.md`](TODO.md) / [`DECISIONS.md`](DECISIONS.md) when possible. Set **Status** → `awaiting_human_approval`. |
| 3 | Human | Review; edit checklist if needed; check **Human approval**; set **Status** → `approved`. |
| 4 | AI | Execute; check off **Checklist**; follow existing doc rules (SoT, `Refs: D-…`, schema regen, tests). Set **Status** → `in_progress` then `complete`. |
| 5 | Human | Delete `active-task.md`. |

---

## Status

`draft` · `awaiting_human_approval` · `approved` · `in_progress` · `complete`

---

## Goal

*(Human: outcome, constraints, links to contract sections if any.)*

---

## Links (optional)

- `PLANNED_INTERFACE.md` §…
- `TODO.md` …
- `DECISIONS.md` …

---

## Doc / contract updates (AI proposes)

*(Files/sections to change; no paste of full normative text — edit the real SoT files.)*

---

## Checklist (AI proposes — human approves)

- [ ] *(prefer rows that mirror or link [`TODO.md`](TODO.md); add `Refs:` there if decision-gated)*

---

## Human approval

- [ ] Checklist approved *(human)*

---

## Execution log (AI)

*(Check items above as completed; optional short notes.)*
