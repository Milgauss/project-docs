# Implementation checklist

**Read:** **`PLANNED_INTERFACE.md`** → **`IMPLEMENTATION_PLAN.md`** → **`DECISIONS.md`** → **this file**. **Future versions:** **[`BACKLOG.md`](BACKLOG.md)** — **`Vx-…`** + open backlog (**not** this v1 checklist unless you add **`TODO_V2.md`**, etc.).

**Interface wins** over the plan. Each § below = **implement → test**. Optional: after v1 ship, use **`TODO_V2.md`** with **`Refs: V2-…`** from **`BACKLOG.md`**.

### Checkpoints: decisions *before* implementation

1. **`Refs: D-…`** → **[`DECISIONS.md`](DECISIONS.md)** (v1 **locked** rows). Do not paste full resolutions here.
2. **No `Refs:` yet** → follow **`PLANNED_INTERFACE.md`** + open **`BACKLOG.md`**; do not invent behavior until the interface is updated. After locking, add **`D-…`** and **`Refs:`**.
3. **Future versions:** locked outcomes before interface merge → **`Vx-…`** in **`BACKLOG.md`**.

---

## Checkpoints (implement → test → …)

**Legend:** **`[ ]`** = not started · **`[x]`** = done. **`Refs:`** = **`DECISIONS.md`** §2–§3.

### 1. Implement — Project scaffold

**Refs:** *(add `D-…` when applicable)*

- [ ] Packaging manifest, package layout, entrypoint **`api-spend`** (or equivalent).
- [ ] Minimal dependencies declared.

### 2. Test — Scaffold

- [ ] Install from repo succeeds.
- [ ] **`api-spend version`** (or equivalent) exits **`0`**.
- [ ] **`api-spend --help`** runs.

### 3. Implement — Contract-shaped stub

- [ ] Primary command emits output matching **`PLANNED_INTERFACE.md`** (shape only), or documented stub until Phase 2.

### 4. Test — Stub

- [ ] Automated test or script asserts stable fields / exit codes per contract.

---

*Add numbered §§ to mirror **`IMPLEMENTATION_PLAN.md`** phases. Mark **`Refs: D-…`** on any checkpoint that depends on a decision row.*
