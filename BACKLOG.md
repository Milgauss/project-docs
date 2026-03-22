# Backlog (future versions: locked decisions + ideas)

**Not the contract until merged into `PLANNED_INTERFACE.md`.** Holds work intended **after the current shipped contract**—**v2, v3+, or not yet version-tied**—until promoted or dropped.

| Layer | Meaning |
|--------|--------|
| **`Vx-…` register** (below) | Decisions **already made** for a **future major**, not yet copied into **`PLANNED_INTERFACE.md`**. |
| **Open sections** (rest of file) | Explorations, options, and todos—**not decided** or not ready to be normative. |

**v1 execution:** **`TODO.md`** + **`DECISIONS.md`** (**`D-…`** only). **`Vx-…`** IDs are for alignment and optional **`TODO_V2.md`** **`Refs:`**—not v1 blockers.

| Doc | Role |
|-----|------|
| [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) | Normative for **shipped** behavior. |
| [`DECISIONS.md`](DECISIONS.md) | v1 **`D-…`**. |
| [`TODO.md`](TODO.md) | v1 checklist. |
| **This file** | **`Vx-…`** + open backlog. |

---

## Locked decisions for future versions (`Vx-…`)

Add a row when you **commit to an outcome** for v2 (or later) but are **not** ready to edit **`PLANNED_INTERFACE.md`**. When you promote: copy behavior into the interface, then note **Promoted** here.

| ID | Topic | Resolution (short) | Promoted to `PLANNED_INTERFACE.md` |
|----|--------|----------------------|-------------------------------------|
| *(example)* **V2-EXAMPLE-FEATURE** | *(short title)* | *(one line)* | — |

**Naming:** **`V{major}-UPPERCASE-SLUG`** (e.g. **`V2-NEW-API`**, **`V3-…`**).

---

## Open backlog

Use headings for themes (integrations, hardening, UX, docs). Capture **options**, **tradeoffs**, and **links** to issues or PRs. When something becomes a locked future decision, add a **`Vx-…`** row above.

### Template: decision log (optional)

| # | Topic | Decision | Date / note |
|---|--------|----------|-------------|
| 1 | *(e.g. retries)* | *(deferred / chosen)* | |

---

## Release / versioning notes (optional)

*How you name releases, deprecations, or migration steps for integrators.*
