# Implementation Plan & Checklist

**Contract:** [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 · **`D-…`:** [`DECISIONS.md`](DECISIONS.md) · **`Vx-…`:** [`BACKLOG.md`](BACKLOG.md) · Retros: [`implementation-notes.md`](implementation-notes.md).

**Agents:** [`README.md`](README.md) for cwd/commands. New repo: if [`BOOTSTRAP.md`](BOOTSTRAP.md) exists → run + update; else fill **§2** before treating stack as locked.

---

## 0. Conventions

**Rules file:** [`.cursor/rules/.cursorrules`](.cursor/rules/.cursorrules)

| Mode | Do |
|------|-----|
| Complex | Short plan first; align before large changes. |
| Simple | Implement; prioritize correctness. |
| Debug | Evidence before guesses; keep functions small. |

**Project:** Scope = task only. **`PLANNED_INTERFACE.md`** changes = intentional + doc update. Secrets → env only; names in contract §8. Never log credentials.

---

## 1. Goals / non-goals

- **Goals:** *(v1 done means …)*
- **Non-goals:** *(out of scope)*

---

## 2. Stack

| Topic | Decision | Notes |
|-------|----------|-------|
| Languages / runtime | *TBD* | e.g. Python 3.x, Node 20+ |
| Packaging | *TBD* | `pyproject.toml` / `package.json` + lockfile |
| Config | *TBD* | |
| Persistence | *TBD* | |
| Testing | *TBD* | pytest, vitest, `node:test`, … |
| Logging / observability | *TBD* | |

User-visible choices → keep aligned with [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md).

---

## 3. Architecture

*(Replace mermaid / table when layout exists.)*

```mermaid
flowchart LR
  A[Client] --> B[Your system]
  B --> C[Dependencies]
```

---

> 🛑 **AGENT STOP:** Do not generate or modify the `## Phase Checklists` below until the Human has explicitly approved Sections 1-3.
> **Design Status:** `[ ] Pending Human Approval` (Change to `[x]` only when human says "approved")

---

## 4. Phase Checklists

*Instructions for Agent: This section is initially shell only during the initial design phase. Once the human approves the architecture above (and the checkbox is `[x]`), you must generate the granular `[ ]` checklist items here based on the design.*

**Legend:** `[ ]` not started · `[x]` done · `Refs:` → `DECISIONS.md` §2–3.

### [ ] Phase 1 — Scaffold

#### [ ] 1.1 Implement

**Refs:** *(e.g. `D-STACK-V1` when locked)*

- [ ] Layout matches §3 Architecture.
- [ ] Packaging setup (+ lockfile) per §2.

#### [ ] 1.2 Test

- [ ] Install from README succeeds clean.
- [ ] Minimal test or smoke from repo root.

### [ ] Phase 2 — *(rename)*

- [ ] *(After `PLANNED_INTERFACE.md` + `PLAN.md` §2 are concrete.)*

---

*Ship `D-…` → move `DECISIONS.md` §3 → §2.*
