# Implementation plan

**Contract:** [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 · **Checklist:** [`TODO.md`](TODO.md) · **`D-…`:** [`DECISIONS.md`](DECISIONS.md) · **`Vx-…`:** [`BACKLOG.md`](BACKLOG.md) · Retros: [`implementation-notes.md`](implementation-notes.md).

**vs `TODO.md`:** Here = stack, boundaries, phase **map**. `TODO.md` = `[ ]`/`[x]` only. Link contract anchors; do not duplicate contract prose.

**Agents:** [`README.md`](README.md) for cwd/commands. New repo: if [`BOOTSTRAP.md`](BOOTSTRAP.md) exists → run + delete; else fill **§2** before treating stack as locked.

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

## 4. Phases

Details in [`TODO.md`](TODO.md).

| Phase | Focus | Deliverable |
|-------|--------|-------------|
| 1 | *TBD* | |
| 2 | *TBD* | |
