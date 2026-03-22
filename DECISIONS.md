# Decisions (v1)

**Normative behavior:** **`PLANNED_INTERFACE.md`**. This file is the **decision register**: what is decided, how far along it is, and what is still open.

**Checklists:** **`TODO.md`** uses **`Refs: D-…`** for rows that map to **`D-…`** IDs below.

---

## How to read this file

| Label | Meaning |
|--------|--------|
| **Locked + shipped** | **`D-…`** row matches **implementation and tests** in the repo. |
| **Locked + pending** | **`D-…`** documents the fork; code or tests may not be finished yet—still follow the row when coding. |
| **Open** | No **`D-…`** yet. Resolve in **`PLANNED_INTERFACE.md`** + **§4** here + open **`BACKLOG.md`** sections. **Future majors:** locked outcomes may live as **`Vx-…`** in **`BACKLOG.md`** until promoted into the interface—they are **not** **`D-…`**. |

---

## 1. Contract & stack (pointers)

| Topic | Where |
|-------|--------|
| *(e.g. output schema, exit codes)* | **`PLANNED_INTERFACE.md`** (list § refs) |
| *(e.g. modules, libraries)* | **`IMPLEMENTATION_PLAN.md`** §2, §5 |

---

## 2. Register — locked + shipped

| ID | Topic | Resolution | Where |
|----|--------|------------|--------|
| **D-RELEASE-NAME** | Distribution + CLI name | **`api-spend`** (same in packaging and docs) | **`PLANNED_INTERFACE.md`** §3; packaging manifest |

*Add rows as you ship. Revise **D-RELEASE-NAME** if the distribution or CLI name changes.*

---

## 3. Register — locked + pending ship

*None.*

---

## 4. Open v1 decisions (no `D-…` yet)

*None.* When you lock a fork: update **`PLANNED_INTERFACE.md`**, add **`D-…`**, add **`Refs:`** on **`TODO.md`**.

---

## 5. Explicitly backlog-only (v2 or non-contract)

Ideas for **v2+** — **`BACKLOG.md`** and draft sections of **`PLANNED_INTERFACE.md`**. **Finalized** future outcomes → **`Vx-…`** in **`BACKLOG.md`**, not **`D-…`**, until you fold them into v1 deliberately.

---

## 6. Adding or changing a `D-…` row

1. Lock behavior in **`PLANNED_INTERFACE.md`** (and **`README.md`** if operators need it).
2. Append or edit a row; use **§2** vs **§3** by whether code already matches.
3. Add or update **`Refs:`** on the relevant **`TODO.md`** checkpoints.

When a **§3** row ships, **move it to §2** and clear the pending note.
