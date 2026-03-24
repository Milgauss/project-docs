# Decisions (v1)

**Norms:** [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md). **`D-…`** register for current major. [`TODO.md`](TODO.md): **`Refs: D-…`** when a checkpoint depends on a row.

## Labels

*(Section numbers below are **this file**, not `PLANNED_INTERFACE.md`.)*

| Label | Meaning |
|--------|--------|
| **§2 shipped** | `D-…` row matches code + tests. |
| **§3 pending** | Locked in contract; implementation may lag — follow row. |
| **Open** | No `D-…` — resolve in `PLANNED_INTERFACE.md`, §4 here, `BACKLOG.md`. Futures: **`Vx-…`** in `BACKLOG.md` until promoted — not `D-…`. |

## 1. Pointers

| Topic | Doc |
|-------|-----|
| Contract | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) |
| Stack / modules | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2–§3 |
| Agent map | [`README.md`](README.md); SoT [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 |

## 2. Locked + shipped

| ID | Topic | Resolution | Where |
|----|--------|------------|--------|
| *(add)* | | | |

## 3. Locked + pending ship

*Empty until contract updates before code.*

## 4. Open (no `D-…`)

*None.* Lock fork → update `PLANNED_INTERFACE.md` → add `D-…` → **`Refs:`** on `TODO.md`.

## 5. Backlog-only (v2+)

Ideas → `BACKLOG.md` / draft interface. Finalized futures → **`Vx-…`** until folded into current major.

## 6. Add/change a `D-…`

1. Lock in `PLANNED_INTERFACE.md` (+ `README.md` only for copy-paste steps).
2. Row in §2 vs §3 by whether code matches.
3. **`Refs:`** on `TODO.md`.

Ship §3 row → move to §2.
