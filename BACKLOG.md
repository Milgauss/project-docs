# Backlog (future versions: locked decisions + ideas)

**Not contract** until merged into [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md).

| Section | Meaning |
|---------|---------|
| `Vx-…` register | Locked outcome for a **future major**, not in the interface yet. One row = one decision; resolution text stays short (no v1 field lists). |
| Open backlog | Ideas — not normative. One short paragraph each; point at contract for v1 behavior. |

v1 execution: [`TODO.md`](TODO.md) + [`DECISIONS.md`](DECISIONS.md) (`D-…`). `Vx-…` = future alignment only.

**Hygiene:** [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §7 (quarterly / release).

---

## Locked decisions for future versions (`Vx-…`)

Add a row when you **commit to an outcome** for v2 (or later) but are **not** ready to edit **`PLANNED_INTERFACE.md`**. When you promote: copy behavior into the interface, then note **Promoted** here.

| ID | Topic | Resolution (short) | Promoted to `PLANNED_INTERFACE.md` |
|----|--------|----------------------|-------------------------------------|
| *(none yet)* | | | |

**Naming:** **`V{major}-UPPERCASE-SLUG`** (e.g. **`V2-NEW-API`**, **`V3-…`**).

---

## Open backlog

When something becomes a locked future decision, add a **`Vx-…`** row above.

### Budget / threshold alerts

Spend limits and notifications — needs a promoted contract section for configuration and how alerts reach the dashboard or caller (transport TBD).

### Local HTTP server mode

Expose query/status over HTTP on localhost so a non-Python dashboard can use `fetch()` — pick framework, bind address, port, and entrypoint when promoted.

### Google Cloud provider

Billing-API adapter via BigQuery export (GCP-billed APIs). Requires export + credentials story in the contract before implementation details belong here.

### Advanced store management

Beyond v1 **`reset`**: date-range delete/re-sync, export/import, retention, schema migrations — specify in interface when any of these become product commitments.

### Non-currency usage metrics

Tokens, requests, emails, bandwidth alongside USD spend — v1 is spend-first (**`PLANNED_INTERFACE.md`** §5–§6). Future: new fields, table(s), or **`query`**/`metric` shape; promote before coding.

### Account balance and credit tracking

Vendor balance/credit APIs (where available) — contract per provider when locked.

### Spend forecasting and pricing analysis

Forecasts, pricing suggestions, anomaly detection — analytical layer on top of stored data; no sync contract change until promoted.

### Tag / label dimensions

User-defined dimensions beyond **`provider`** + **`service`** — needs **`group_by`** / config rules in the contract.
