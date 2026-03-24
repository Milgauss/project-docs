# Planned interface (design contract)

**Contract revision:** `YYYY-MM-DD` — template scaffold. **Bump** date and add a **short note** (what changed) whenever you edit **normative** content (§3–§8 behavior, models, env names). Then update dependents in the same change set where they apply: [`README.md`](README.md) commands, generated schema / OpenAPI, tests.

**Template:** Replace **Your Project**; add §3–§8 when design exists. Layout: [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

**Agents**

- Read [`README.md`](README.md) **For coding agents** first.
- **§0** = SoT table. Conflict → **this file wins**; fix code or this file on purpose.
- If [`BOOTSTRAP.md`](BOOTSTRAP.md) exists: it may touch **§0** (artifact paths/regen) + README commands only — not §1–§7.
- **`active-task.md`** (optional, gitignored): mission + checklist only — **not** SoT; see [`active-task.template.md`](active-task.template.md).
- Do not use `README.md` as a second spec for behavior ([§0](PLANNED_INTERFACE.md#sources-of-truth)).

**Related:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DECISIONS.md`](DECISIONS.md) · [`TODO.md`](TODO.md) · [`BACKLOG.md`](BACKLOG.md)

---

<a id="sources-of-truth"></a>

## 0. Sources of truth

Secondary docs **link** here; do not restate normative behavior in `README.md`, `IMPLEMENTATION_PLAN.md`, or `implementation-notes.md` when this file defines it.

| Kind of fact | Authoritative | Where |
|--------------|---------------|--------|
| Behavior, public models, errors | This file | §3–§7 (when present) |
| Env var **names** / required / purpose | This file | §8 |
| Install, test, ops **commands** | [`README.md`](README.md) | For coding agents |
| Stack, modules, phases | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | §2–§4 |
| Checklist | [`TODO.md`](TODO.md) | — |
| **`D-…`** | [`DECISIONS.md`](DECISIONS.md) | §2–§3 |
| **`Vx-…`**, v2+ ideas | [`BACKLOG.md`](BACKLOG.md) | — |
| Retros | [`implementation-notes.md`](implementation-notes.md) | non-normative |
| Optional generated schema / OpenAPI | Path you record | **Python+Pydantic:** `python scripts/export_public_schema.py` (`PUBLIC_PACKAGE`). **Node:** your pipeline — record **file** + **regen** here and in [`README.md`](README.md). |

*`active-task.md` is intentionally **not** in this table — operational scratch only ([`active-task.template.md`](active-task.template.md)).*

---

## 1. Who uses this interface?

| Actor | Goal |
|-------|------|
| *(add)* | |

---

## 2. Design principles

*(add or link)*

---

## 3. *(e.g. public API, integrations)*

*(add)*

---

## 4. *(e.g. configuration)*

---

## 5. *(e.g. operations)*

---

## 6. *(e.g. data shapes)*

---

## 7. Errors and edge cases

*(add)*

---

## 8. Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| *(add)* | | |

---

*Release: bump **Contract revision** at top; sync [`CHANGELOG.md`](CHANGELOG.md).*
