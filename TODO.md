# Implementation checklist

**Agents — read order:** [`README.md`](README.md) → [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 → [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) → **this file** → [`DECISIONS.md`](DECISIONS.md) when **`Refs: D-…`** → optional [`BACKLOG.md`](BACKLOG.md), [`implementation-notes.md`](implementation-notes.md).

If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists, finish it before deep product work (see README).

**vs `IMPLEMENTATION_PLAN.md`:** Only **this file** uses `[ ]` / `[x]`. **Contract > plan.** Link § anchors; do not paste long specs.

**Before implement**

1. `Refs: D-…` → [`DECISIONS.md`](DECISIONS.md) §2–§3 (do not paste full resolution).
2. No `Refs:` → follow `PLANNED_INTERFACE.md` + `BACKLOG.md`; do not invent behavior; then add `D-…` + `Refs:`.

---

## Checkpoints

**Legend:** `[ ]` not started · `[x]` done · `Refs:` → `DECISIONS.md` §2–3.

### [ ] Phase 1 — Scaffold

#### [ ] 1.1 Implement

**Refs:** *(e.g. `D-STACK-V1` when locked)*

- [ ] Layout matches [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §3.
- [ ] `pyproject.toml` and/or `package.json` (+ lockfile) per §2.

#### [ ] 1.2 Test

- [ ] Install from README succeeds clean.
- [ ] Minimal test or smoke from repo root.

### [ ] Phase 2 — *(rename)*

- [ ] *(After `PLANNED_INTERFACE.md` + `IMPLEMENTATION_PLAN.md` §2 are concrete.)*

---

*Ship `D-…` → move `DECISIONS.md` §3 → §2.*
