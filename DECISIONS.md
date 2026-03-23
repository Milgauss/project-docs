# Decisions (v1)

Norms: [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md). This file = v1 `D-…` register + status.

[`TODO.md`](TODO.md): `Refs: D-…` where a checkpoint depends on a row here.

---

## How to read this file

| Label | Meaning |
|--------|--------|
| **Locked + shipped** | **`D-…`** row matches **implementation and tests** in the repo. |
| **Locked + pending** | **`D-…`** is decided in the contract; implementation may still be in progress—follow the row when coding. |
| **Open** | No **`D-…`** yet. Resolve in **`PLANNED_INTERFACE.md`**, section 4 here, and open **`BACKLOG.md`** sections. **Future majors:** locked outcomes may live as **`Vx-…`** in **`BACKLOG.md`** until promoted into the interface—they are **not** **`D-…`**. |

---

## 1. Contract & stack (pointers)

| Topic | Where |
|-------|--------|
| Contract (API, models, providers, errors, env) | [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) |
| Stack and module layout | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2–§3 |
| SQLite (v1) | `src/api_spend/store.py`; store paths in contract §8 and `src/api_spend/config.py` |
| Agent navigation + code map | [`README.md`](README.md) (**For coding agents**); SoT [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) **§0** |
| Phase 8–9 `D-…` (shipped) | §2: facade + sync window + caps + **`D-LOGGING-V1`** |

---

## 2. Register — locked + shipped

| ID | Topic | Resolution | Where |
|----|--------|------------|--------|
| **D-RELEASE-NAME** | Distribution / package name | **`api-spend`** (same in packaging and docs; v1 surface is the Python API, not a CLI) | **`PLANNED_INTERFACE.md`** §4.1; `pyproject.toml` |
| **D-PYTHON-VERSION** | Minimum Python version | **Python 3.11+** (`requires-python` in `pyproject.toml`). | **`IMPLEMENTATION_PLAN.md`** §2; `pyproject.toml` |
| **D-CONFIG-FORMAT** | Config file format | **YAML** (`config.yaml`); load via `api_spend.load_config` / `AppConfig`. | **`PLANNED_INTERFACE.md`** §4.2; `src/api_spend/config.py` |
| **D-LOOKBACK** | First-sync lookback | Default **60 days** (`sync.lookback_days`). Billing APIs backfill; snapshot providers only get “now” on first sync (`PLANNED_INTERFACE.md` §5.1). | **`PLANNED_INTERFACE.md`** §5.1; `src/api_spend/config.py` |
| **D-V1-PROVIDERS** | v1 provider set | **Billing-API:** OpenAI, Anthropic, Bright Data. **Snapshot-based:** Resend, Brave Search. | **`PLANNED_INTERFACE.md`** §3; `src/api_spend/providers/` |
| **D-CURRENCY-V1** | Currency handling | v1 assumes **USD** for all providers. No conversion. Query results use **`V1_QUERY_CURRENCY`** (`"USD"`). | **`PLANNED_INTERFACE.md`** §5.2; `src/api_spend/query.py` |
| **D-QUERY-BUCKETS-V1** | Week / month bucket boundaries | **`week`:** ISO weekday alignment (Monday starts a segment); first segment begins at `start` (may be shorter than seven days). **`month`:** calendar months intersected with `[start, end)` (exclusive `end`). **`day`:** each calendar day in range. | **`PLANNED_INTERFACE.md`** §5.2; `src/api_spend/query.py` (`iter_bucket_periods`) |
| **D-BILLING-FETCH-V1** | Billing adapter errors | **`BillingApiProvider.fetch_costs`** → **`FetchCostsResult(records, error)`**; HTTP/API failures set **`error`**, empty **`records`**, no raise. | **`PLANNED_INTERFACE.md`** §3.1; **`IMPLEMENTATION_PLAN.md`** §3; `providers/base.py` |
| **D-FACADE-INIT-V1** | `ApiSpend.__init__` | Optional injected **`SpendStore`** (`store=`); otherwise open default DB from store path. **`require_credentials`** mirrors **`load_config`** (default **`True`**). Optional shared **`httpx.Client`** via **`http_client=`** for tests (not required by the contract). | **`PLANNED_INTERFACE.md`** §4.3; `src/api_spend/client.py` |
| **D-BILLING-SYNC-WINDOW-V1** | Billing `sync` range + metadata + counts | UTC calendar **`[start, end)`** per **`PLANNED_INTERFACE.md`** §5.1; **`sync_metadata`** updated **only on per-provider success**; **`ProviderSyncStatus.records_added`** = spend rows inserted/replaced that sync. | **`PLANNED_INTERFACE.md`** §5.1; `src/api_spend/client.py` |
| **D-PROVIDER-CAPS-V1** | `ProviderCapabilities` + snapshot services | Static capabilities per adapter type (**§5.3**). Snapshot **`SpendRecord.service`**: **`resend`→`emails`**, **`brave_search`→`requests`**. | **`PLANNED_INTERFACE.md`** §5.1, §5.3; `src/api_spend/client.py` |
| **D-LOGGING-V1** | Stdlib logging | Loggers under **`api_spend.*`**; **INFO** for sync lifecycle + per-provider failure signal; **DEBUG** for query windows, billing fetch errors, successful per-provider record counts, store close; **no** **`API_SPEND_…`** log-level env in **§8**; never log secrets. | **`PLANNED_INTERFACE.md`** §4.4; `client.py`, `store.py`, `config.py`, `snapshot_sync.py` |

*Add rows as you ship. Revise **D-RELEASE-NAME** if the distribution or package name changes.*

---

## 3. Register — locked + pending ship

*No rows.* Use this section when the contract is updated and **`D-…`** is locked, but implementation or tests have not caught up yet — then move the row to **§2** when shipped.

---

## 4. Open v1 decisions (no `D-…` yet)

*None.* When you lock a fork: update **`PLANNED_INTERFACE.md`**, add **`D-…`**, add **`Refs:`** on **`TODO.md`**.

---

## 5. Explicitly backlog-only (v2 or non-contract)

Ideas for **v2+** — **`BACKLOG.md`** and draft sections of **`PLANNED_INTERFACE.md`**. **Finalized** future outcomes → **`Vx-…`** in **`BACKLOG.md`**, not **`D-…`**, until you fold them into v1 deliberately.

---

## 6. Adding or changing a `D-…` row

1. Lock behavior in **`PLANNED_INTERFACE.md`** (and **`README.md`** if operators need it).
2. Append or edit a row; use **section 2** vs **section 3** by whether code already matches.
3. Add or update **`Refs:`** on the relevant **`TODO.md`** checkpoints.

When a **section 3** row ships, **move it to section 2** and remove it from **section 3**.
