# Planned interface (design contract)

**API Spend** — normative contract (behavior, shapes, semantics). Module layout: [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §3.

**Agents:** Start [`README.md`](README.md) **For coding agents** (cwd, terminal blocks, test map). **§0** = SoT table (which doc owns each fact type). Facade: `src/api_spend/client.py` → `api_spend.ApiSpend`; read **§4.3**, **§4.4**, **§5.1–§5.6**. Run `pytest` from repo root. Shipped `D-…`: see [`DECISIONS.md`](DECISIONS.md) §2 (e.g. `D-FACADE-INIT-V1`, `D-BILLING-SYNC-WINDOW-V1`, `D-PROVIDER-CAPS-V1`, `D-LOGGING-V1`).

**Also:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DECISIONS.md`](DECISIONS.md) §2–§3 · [`TODO.md`](TODO.md) · [`BACKLOG.md`](BACKLOG.md) (`Vx-…`).

**Navigate:** §0 SoT · §3 providers · §4 install + `ApiSpend` + logging · §5 ops · §6 spend model · §7 errors · §8 env (**§8.1–§8.3**).

**Contract revision (last doc/code alignment pass):** 2026-03-23 — bump when you intentionally change normative sections or public API shapes and have updated dependents (`README.md` commands, `schemas/public_pydantic_schemas.json`, tests).

---

<a id="sources-of-truth"></a>

## 0. Sources of truth

Do **not** restate normative behavior in [`README.md`](README.md), [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md), or [`implementation-notes.md`](implementation-notes.md) when this file already defines it. Secondary docs **link** here (§ anchor). If something disagrees, **this file wins** (then fix code or this file deliberately).

| Kind of fact | Authoritative doc | Section(s) |
|--------------|-------------------|------------|
| Behavior, API semantics, public models, errors | **This file** (`PLANNED_INTERFACE.md`) | §3–§7, model blocks in §5–§6 |
| Environment variable **names**, required-if, purpose | **This file** | **§8** |
| Copy-paste **commands** for install, pytest, live tests | [`README.md`](README.md) | **For coding agents**, **Live API tests** |
| **Logging** (stdlib hierarchy, caller configures handlers / levels) | **This file** | **§4.4** (no log-level env var in **§8**) |
| Module layout, stack, build phases | [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | §2–§3, phase table §4 |
| Checklist, shipped vs next | [`TODO.md`](TODO.md) | Phases 1–9 (v1); use for future checkpoints |
| Locked **`D-…`** resolutions | [`DECISIONS.md`](DECISIONS.md) | §2–§3 |
| v2+ ideas (not v1 contract) | [`BACKLOG.md`](BACKLOG.md) | **`Vx-…`** |
| Historical friction / retros only | [`implementation-notes.md`](implementation-notes.md) | (non-normative) |
| Example YAML only (not rules) | [`config.example.yaml`](config.example.yaml) | (comments → §3–§4, §8) |
| Machine-checked JSON Schema for public Pydantic models | Repo root `schemas/public_pydantic_schemas.json` | `python scripts/export_public_schema.py`; CI: `tests/test_public_schema_snapshot.py` |

---

## 1. Who uses this interface?

| Actor | Goal |
|-------|------|
| **Dashboard front-end** | Import `api_spend`; receive uniform spend data over arbitrary time ranges without knowing provider-specific quirks. |
| **Human operator** | Configure providers and credentials; trigger syncs; check status. |
| **Automation / scripts** | Periodic sync via cron or scheduler; programmatic queries for alerts or reports. |

**Dashboard implementers:** **`query`** returns **USD** buckets from the store, not live vendor usage counters. For **Resend / Brave**, the current vendor counter is on **`sync`** (**`ProviderSyncStatus.counter_observed`**). Read **§5.1** (dashboard note), **§5.2**, and **§3.2** before mapping fields to UI labels.

---

## 2. Design principles

1. **Dashboard developer knows one schema.** All provider differences are hidden behind a single spend-record model. The dashboard never imports a provider adapter or parses provider-specific responses.
2. **Time-series first.** Every query returns data oriented around time buckets so it can be rendered directly as a chart or table without client-side aggregation.
3. **Honest about coverage.** When a provider cannot supply data for part of a requested range, the response says so explicitly (gaps, estimated vs authoritative flags) rather than silently returning zeros or omitting points.
4. **Partial success over total failure.** If three of four providers sync successfully, the caller gets three providers' data plus a per-provider error for the fourth—not a top-level exception.
5. **Secrets in environment variables only.** API keys are never passed as function arguments in normal use and **never** appear in the YAML file; they use the names in §8.
6. **Persistence is the package's job.** The package owns a local data store (format is an implementation detail). The dashboard reads from it via the query API; it never touches the store directly.

---

## 3. Supported providers (v1)

**`D-V1-PROVIDERS`** in [`DECISIONS.md`](DECISIONS.md).

### 3.1 Billing-API providers

These providers expose a dedicated billing or cost endpoint that supports date-range queries and returns reported costs.

| Provider | Endpoint | Date range | Granularity | Service breakdown | Credential env var |
|----------|----------|-----------|-------------|-------------------|--------------------|
| **OpenAI** | `GET /v1/organization/costs` | Yes (`start_time`/`end_time` Unix sec) | Daily (`1d`) | By project + line item (`group_by`) | `API_SPEND_OPENAI_API_KEY` ([Administrator API key](https://platform.openai.com/settings/organization/admin-keys), not a default/project key) |
| **Anthropic** | `GET /v1/organizations/cost_report` | Yes (`starting_at`/`ending_at` RFC 3339) | Daily (`1d`) | Workspace / model / cost & token types (§ below) | `API_SPEND_ANTHROPIC_API_KEY` (`sk-ant-admin…`) |
| **Bright Data** | `GET /zone/cost` | Yes (`from`/`to`) | Daily / monthly | Zone + `back_dN` / `back_mN` (§ below) | `API_SPEND_BRIGHTDATA_API_KEY` |

For billing-API providers, `sync` fetches since the last successful sync (or **`lookback_days`** on first run) and stores **reported** costs. `SpendBucket.coverage` is **`"complete"`** when the full bucket is covered.

**OpenAI:** **`options.organization_id`** → **`OpenAI-Organization`** ([org id](https://platform.openai.com/settings/organization/general)). **`service`:** lowercased **`line_item`**, or **`{project_id}:{line_item}`** if **`project_id`** is set; missing line item → **`unattributed`**. HTTP/API failures → **`FetchCostsResult`** (**`D-BILLING-FETCH-V1`**); no raise.

**Anthropic:** Key must start with **`sk-ant-admin`** (otherwise **`fetch_costs`** / **`validate_credentials`** fail without calling the API when possible). **`anthropic-version`: `2023-06-01`**. Cost report **`group_by`** is sent as repeated query keys **`group_by[]=workspace_id`** and **`group_by[]=description`** (not a single array param). **`amount`** is minor units (e.g. cents) → ÷ 100 for USD. **`service`:** lowercased colon-joined present fields among **`workspace_id`**, **`model`**, **`cost_type`**, **`token_type`**; else lowercased **`description`**; else **`unattributed`**. Skip non-USD rows.

**Bright Data:** Required **`options.zone`** (query param **`zone`**). **`from`** / **`to`** = UTC **`00:00:00.000Z`** for the **`start`** / **`end`** dates of **`fetch_costs(start, end)`** (**`[start, end)`**, **`end`** exclusive). Responses vary by product: **`back_dN`** (daily) and/or **`back_mN`** (monthly) under an id key (or **`data`**), **or** a **`custom`** object with **`cost`**, optional **`bw`**, and **`range.from` / `range.to`** (often **`DD-MMM-YYYY`**). **`service`** = **`{zone}:{back_dN}`**, **`{zone}:{back_mN}`**, or **`{zone}:custom`** (zone lowercased). **`back_dN`** → **`back_d0`** = UTC day **`end - 1 day`**, **`back_d1`** = **`end - 2 days`**, … **`back_mN`** → first day of that calendar month when it intersects **`[start, end)`**. **`custom`** → one row: **`date`** from **`range.from`** when it parses and falls in **`[start, end)`**, else **`start`**; amount = **`custom.cost`**. Merge order: prefer **daily** if any daily **`cost` ≠ 0**; else **monthly** if any monthly **`cost` ≠ 0**; else **custom** if present; else daily rows (possibly all zero) or **`[]`**.

### 3.2 Snapshot-based providers

These providers have **no billing API**. Usage counters are available only as response headers or quota endpoints that report current-period totals without historical breakdown. The package derives cost by periodically recording the counter and multiplying usage deltas by known per-unit pricing.

| Provider | Usage source | Counter | Pricing (for cost estimation) | Credential env var |
|----------|-------------|---------|-------------------------------|--------------------|
| **Resend** | `GET https://api.resend.com/emails` (**`limit=100`**), **`Accept: application/json`**, library **`User-Agent`**. Counter: **`x-resend-monthly-quota`** → **`quota_period`** `YYYY-MM`; else **`x-resend-daily-quota`** → **`YYYY-MM-DD`** ([docs](https://resend.com/docs/api-reference/rate-limit)). If both quota headers are absent, **paginate** (`after`, **`has_more`**) and count **`created_at`** in the **current UTC month** → **`quota_period`** `YYYY-MM`. **`ratelimit-*`** without **`x-resend-*`** is **HTTP** throttling only, not send quota. List-derived counts may not match vendor quota (e.g. mail not visible on this list). | Emails (quota or list-derived) | Plan-dependent (`options.plan` / `per_email_usd`) | `API_SPEND_RESEND_API_KEY` |
| **Brave Search** | **`X-RateLimit-Limit`** / **`X-RateLimit-Remaining`** as **comma-separated**, **positionally paired** windows ([Brave rate limiting](https://api-dashboard.search.brave.com/documentation/guides/rate-limiting)). **`X-RateLimit-Policy`** (`limit;w=seconds` per segment): use the segment with the **largest `w=`** among **`limit > 0`**; if policy is missing, use the segment with the **largest `limit`**. Used requests = **`limit − remaining`** for that segment. | Requests used (chosen window) | $5 / 1,000 requests | `API_SPEND_BRAVE_API_KEY` |

**Behavior:**

- `sync` makes a lightweight API call (Resend: `GET /emails` — headers or paginated list fallback; Brave: cheapest available endpoint) to read the current usage counter, records a timestamped snapshot, and stores the delta since the previous snapshot as an **estimated** spend record.
- `SpendBucket.coverage` is always `"estimated"` for these providers. `ProviderCapabilities.supports_date_range` is `False`.
- If a sync is missed, the next sync captures the accumulated delta as a single record spanning the gap — the package cannot retroactively split it into daily buckets.
- Pricing assumptions are configured per provider in the config file (or defaulted from known published rates). If the provider changes pricing mid-period, estimates may drift.

---

## 4. Installation and setup

### 4.1 Package name

**`api-spend`** (`D-RELEASE-NAME` in [`DECISIONS.md`](DECISIONS.md)). **PyPI:** `pip install api-spend` when the package is published there. **Private / source:** editable install (`pip install -e .`), path/submodule checkout, or `pip install "git+https://…@v…"` — see [`README.md`](README.md) **For dashboard integrators**.

Import as:

```python
import api_spend
```

### 4.2 Configuration

A single YAML file defines which providers to track and how to reach them (`D-CONFIG-FORMAT` in [`DECISIONS.md`](DECISIONS.md)).

**Default path:** `~/.config/api-spend/config.yaml` (override with `API_SPEND_CONFIG` env var).

```yaml
sync:
  lookback_days: 60          # how far back to fetch on first sync (default: 60)

providers:
  - name: openai
    options:
      organization_id: org-xxxxxxxx   # required for Costs API (§3.1)
  - name: anthropic
  - name: brightdata
    options:
      zone: my_zone   # required — passed to GET /zone/cost
  - name: resend
    options:
      plan: "pro"            # used to select per-unit pricing for cost estimation
  - name: brave_search
```

**Credentials:** names are listed in **§8** (and §3). They are **not** derived from YAML `providers[].name` (e.g. `brave_search` → `API_SPEND_BRAVE_API_KEY`). Nothing secret belongs in the YAML file.

**Empty `providers` list:** YAML may legally list **zero** providers (valid config for **`load_config`** / **`ApiSpend`**). **`sync`** then returns **`SyncResult`** with **`providers=[]`** and performs no provider calls. **`query`** and **`run_query`** require a **non-empty** configured provider set — see **§5.2** and **`ValueError`** in **§7.2**. Dashboards that call **`query`** should ensure at least one provider is configured.

### 4.3 Initialization

```python
from api_spend import ApiSpend

client = ApiSpend()            # default config path, default store path
client = ApiSpend(config_path) # explicit config path
# Optional (keyword-only, for tests or advanced use):
# ApiSpend(store=existing_spend_store)
# ApiSpend(..., require_credentials=False)  # mirror load_config; default True
```

The constructor validates config, opens the local **`SpendStore`** (default path from **`API_SPEND_STORE_PATH`** / implementation default unless **`store=`** is injected), and applies **`require_credentials`** like **`load_config(..., require_credentials=…)`** (default **`True`**). It will **not** call provider APIs on init.

**Implementation note (non-normative):** tests may pass a shared **`httpx.Client`** (e.g. with **`MockTransport`**) as **`http_client=`** so all adapters use the same mock; production callers omit it and adapters construct their own clients.

### 4.4 Logging (observability)

v1 uses the stdlib **`logging`** package for library observability. Records use a hierarchy under **`api_spend`** (e.g. **`api_spend.client`**, **`api_spend.store`**) — exact coverage evolves with releases but stays under that prefix.

**Caller-configured:** The package does **not** attach handlers or set levels by default and does **not** define a library-specific env var for log level in **§8**. Integrators enable output by configuring **`logging`** in the application (e.g. **`basicConfig`**, dict config, or host framework integration). Typical mapping: **INFO** for high-level events (e.g. sync start/end, per-provider outcomes, store open/close); **DEBUG** for verbose traces. Logs must **not** include secrets (API keys, raw auth headers, or full credential-bearing responses).

---

## 5. Core operations (v1)

**Shipped surface:** **`ApiSpend`** (**`sync`**, **`query`**, **`providers`**, **`status`**, **`validate`**, **`reset`**) plus the lower-level **`load_config`**, **`SpendStore`**, **`run_query`** helpers from **§4** ([README](README.md)).

### 5.1 `sync`

Fetch the latest cost data from all (or a subset of) configured providers and persist it locally.

```python
result: SyncResult = client.sync()
result: SyncResult = client.sync(providers=["openai", "anthropic"])
```

**Behavior:**

- **Zero configured providers:** if the YAML **`providers`** list is empty, **`sync`** returns **`SyncResult(providers=[], synced_at=…)`** and does not call any provider APIs.
- Calls each provider's billing/usage API for the period since the last successful sync (billing), or runs snapshot logic (Resend, Brave Search).
- **Billing-API providers — date range (UTC calendar dates, `[start, end)` with exclusive `end`):** Let **`end_date`** be the **UTC date** of the sync run (wall-clock **`synced_at`** in UTC). **First sync** for that provider (no **`sync_metadata`** row, or after **`reset`** for that provider): **`start = end_date − lookback_days`**, **`end = end_date`**, using **`sync.lookback_days`** from config (default **60**). **Later syncs:** if stored **`latest_date`** is **`L`**, **`start = L + 1 day`**, **`end = end_date`**. If **`start >= end`**, the fetch is empty for that run. Adapters receive the same **`start`/`end`** semantics as today’s **`fetch_costs(start, end)`**.
- **Snapshot-based providers:** no date-range fetch; **`run_snapshot_sync`** (or equivalent) at sync time. Estimated **`SpendRecord.service`** is fixed: **`resend`** → **`emails`**, **`brave_search`** → **`requests`**.
- **`sync_metadata`:** updated **`last_synced`** and **`latest_date`** for a provider **only when that provider’s sync succeeds** (`ok` is true — no adapter-reported fetch/snapshot error). On failure, metadata is unchanged so the next sync retries the appropriate window.
- Normalizes responses into the canonical spend model (§6).
- Persists new records to the local store, deduplicating against existing data.
- Returns a `SyncResult` summarizing what happened per provider.

**`ProviderSyncStatus.records_added`:** number of **`spend_records`** rows **inserted or replaced** for that provider during this sync (after dedupe / **`INSERT OR REPLACE`** semantics in the store).

**`ProviderSyncStatus.counter_observed`:** for **snapshot** providers (**`resend`**, **`brave_search`**), the vendor usage **counter** read during this sync (e.g. emails or requests used in the chosen quota window — see §3.2 for how that counter is derived). **`None`** for billing-API providers and when the counter could not be read (e.g. some error paths).

**Dashboard: what `sync` vs `query` mean (especially snapshot providers):**

- **`SyncResult`** describes **this sync run only** (point in time **`synced_at`**). It is the right place to read **`counter_observed`** for a **“current usage”** style metric (e.g. “~N emails in the active Resend quota window right now”). That number is **not** a full history, **not** a lifetime total, and **not** carried into **`query`**.
- **`QueryResult`** reads the **local store** and returns **`SpendBucket.amount`** in **USD** (v1 single currency). Buckets reflect **persisted `SpendRecord` rows** — authoritative billing costs for API-backed providers, **estimated** costs for snapshot providers when deltas created rows (§3.2). **`query` does not expose raw email or request counts**; do not infer “emails sent” from **`amount`** without dividing by your configured rate (fragile and not recommended as a primary metric).
- For **Resend / Brave**, the **first** successful sync often records **`counter_observed`** but **`records_added == 0`** (baseline snapshot only). Until a later sync sees a **counter delta**, **`query`** may show **no** snapshot USD in the range while **`sync`** still reports the live counter — both can be correct simultaneously.
- With **`group_by=None`**, each bucket **`amount`** is the **sum across all included providers**. Use **`group_by="provider"`** (or **`["provider", "service"]`**) to split billing vs snapshot **estimated** lines on charts.

**`SyncResult` shape** (all models are Pydantic `BaseModel`; the dashboard can call `.model_dump()` / `.model_dump_json()` on any return type):

```python
class ProviderSyncStatus(BaseModel):
    provider: str
    ok: bool
    records_added: int
    latest_date: date | None     # most recent date covered (spend rows); snapshot may stay None until a spend row exists
    error: str | None            # human-readable; None when ok
    counter_observed: int | None # snapshot providers only; else None

class SyncResult(BaseModel):
    providers: list[ProviderSyncStatus]
    synced_at: datetime           # UTC wall-clock time of this sync
```

### 5.2 `query`

Return spend data for a time range, optionally filtered and grouped.

```python
result: QueryResult = client.query(
    start=date(2025, 1, 1),
    end=date(2025, 4, 1),          # exclusive upper bound
    granularity="day",             # "day" | "week" | "month"
    providers=None,                # None = all; or list of names
    group_by=None,                 # None | "provider" | "service" | ["provider", "service"]
)
```

**Parameters:**

| Parameter | Type | Default | Meaning |
|-----------|------|---------|---------|
| `start` | `date` | required | Inclusive start of range. |
| `end` | `date` | required | Exclusive end of range. |
| `granularity` | `str` | `"day"` | Bucket size: `"day"`, `"week"`, `"month"`. |
| `providers` | `list[str] \| None` | `None` | Subset filter. `None` means every configured provider (see below). |
| `group_by` | `str \| list[str] \| None` | `None` | One or both of `"provider"`, `"service"`, or `None` for a single total per bucket. |

**`run_query` (lower-level API):** The package also exposes `run_query(store, start, end, *, configured_providers, …)` with the same bucketing semantics as **`ApiSpend.query`**. Pass the full provider name list from config as `configured_providers`; gaps and `providers=None` use that scope. `providers`, if set, must be a subset of `configured_providers`.

**Non-empty configured scope:** **`query`** and **`run_query`** require **`configured_providers`** to contain **at least one** provider name. If the config lists no providers, **`ApiSpend.query`** raises **`ValueError`** (same as **`run_query(..., configured_providers=[])`**). This is intentional: there is no defined bucket/gap semantics for “query with zero providers.”

**`QueryResult` shape:**

```python
class SpendBucket(BaseModel):
    period_start: date
    period_end: date               # exclusive
    group: dict[str, str] | None   # grouping key→value pairs, or None when ungrouped
    amount: Decimal                # total spend in this bucket+group
    currency: str                  # ISO 4217, e.g. "USD"
    coverage: str                  # "complete" | "partial" | "estimated"

class QueryResult(BaseModel):
    buckets: list[SpendBucket]
    providers_included: list[str]
    gaps: list[GapInfo]            # ranges with missing data

class GapInfo(BaseModel):
    provider: str
    start: date
    end: date                      # exclusive
    reason: str                    # e.g. "provider not synced before 2025-02-15"
```

**Semantics:**

- Buckets are **contiguous** and cover the full `[start, end)` range for each group combination, even if the amount is zero. The dashboard can rely on this for axis alignment without filling gaps itself.
- **`day`:** one bucket per calendar day in `[start, end)`.
- **`week`:** buckets align to **ISO weeks** (each segment starts on Monday). The **first** bucket starts at `start` and may span fewer than seven days; later buckets run Monday-to-Monday or until `end`, whichever is earlier.
- **`month`:** one bucket per **calendar month** intersected with `[start, end)`; each `period_end` is exclusive.
- When `group_by` is a list (e.g. `["provider", "service"]`), `SpendBucket.group` is a dict like `{"provider": "openai", "service": "gpt-4o"}`. When it is a single string, the dict has one key. When `None`, `group` is `None`.
- When data is missing for part of a bucket, that bucket's `coverage` is `"partial"` or `"estimated"`, and a corresponding entry appears in `gaps`.
- Amounts within a single query are always in the **same currency**. V1 assumes everything is USD.
- **Snapshot providers (§3.2):** rows in the store are **estimated** spend from counter **deltas**; **`coverage`** for those segments is **`"estimated"`**. Missing prior syncs or **zero delta** runs produce **gaps** or **zero** amounts even if **`sync.counter_observed`** on the latest run is non-zero (see §5.1 dashboard note).

### 5.3 `providers`

List configured providers and their sync status.

```python
info: list[ProviderInfo] = client.providers()
```

```python
class ProviderInfo(BaseModel):
    name: str
    configured: bool               # credentials and config present
    last_synced: datetime | None   # UTC; None if never synced
    earliest_data: date | None     # oldest record in store
    latest_data: date | None       # newest record in store
    capabilities: ProviderCapabilities

class ProviderCapabilities(BaseModel):
    supports_date_range: bool      # can the API fetch arbitrary date ranges?
    native_granularity: str        # finest granularity the API provides, e.g. "day"
    supports_service_breakdown: bool  # does the API break costs down by service/model?
```

**Capabilities and `ProviderInfo` fields:** **`ProviderCapabilities`** are **static** per adapter type (not read from the network): **billing** providers (**`openai`**, **`anthropic`**, **`brightdata`**) use **`supports_date_range=True`**, **`native_granularity="day"`**, **`supports_service_breakdown=True`**. **Snapshot** providers (**`resend`**, **`brave_search`**) use **`supports_date_range=False`**, **`native_granularity="snapshot"`**, **`supports_service_breakdown=True`** (service is the fixed snapshot label above). **`last_synced`**, **`earliest_data`**, and **`latest_data`** come from **`sync_metadata`** and **`spend_records`** in the store.

### 5.4 `status`

Quick health check — useful for a dashboard status bar.

```python
s: Status = client.status()
```

```python
class Status(BaseModel):
    configured_providers: int
    synced_providers: int
    last_sync: datetime | None     # most recent sync across all providers
    store_size_bytes: int | None
```

**`store_size_bytes`:** from the store’s **approximate** byte size (e.g. **`PRAGMA page_count` × `page_size`**). Use **`None`** when not meaningful (e.g. **`:memory:`** database).

### 5.5 `validate`

Check configuration and credentials without fetching data.

```python
result: ValidateResult = client.validate()
result: ValidateResult = client.validate(check_connectivity=True)
```

```python
class ProviderValidation(BaseModel):
    provider: str
    config_ok: bool                # config section is well-formed
    credentials_ok: bool           # required env var(s) are set
    reachable: bool | None         # None if not tested; True/False after a lightweight probe
    error: str | None

class ValidateResult(BaseModel):
    providers: list[ProviderValidation]
    config_path: str               # resolved path that was loaded
```

| Parameter | Type | Default | Meaning |
|-----------|------|---------|---------|
| `check_connectivity` | `bool` | `False` | When `True`, performs a minimal read-only probe per provider and sets `reachable`; when `False`, only validates config shape and env vars (`reachable` stays `None`). |

### 5.6 `reset`

Remove stored data. Useful when data is bad, a provider is removed, or the user wants a fresh start.

```python
client.reset()                            # clear everything
client.reset(providers=["openai"])        # clear one provider's data only
```

**Behavior:**

- Deletes spend records (and snapshot history for snapshot-based providers) matching the filter.
- Does **not** delete configuration or the store file itself.
- Next `sync` for a reset provider behaves like a first sync (applies `lookback_days`).

---

## 6. Canonical spend model

All provider data is normalized to this model before storage. The dashboard never sees raw provider shapes.

| Field | Type | Meaning |
|-------|------|---------|
| `provider` | `str` | Lowercase provider identifier, e.g. `"openai"`, `"anthropic"`, `"brightdata"`. |
| `service` | `str` | Provider-defined label, lowercased. Billing adapters: §3.1 (OpenAI line item / project; Anthropic workspace fields; Bright Data `zone:back_dN` / `zone:back_mN` / `zone:custom`). |
| `date` | `date` | The calendar day this cost applies to (provider's billing day, UTC). |
| `amount` | `Decimal` | Cost for this provider + service + date. |
| `currency` | `str` | ISO 4217 code. |

**`SpendRecord` shape** (same Pydantic `BaseModel` stack as §5; used for storage and provider normalization — `query` still returns aggregated `SpendBucket`s, not raw records):

```python
class SpendRecord(BaseModel):
    provider: str
    service: str
    date: date
    amount: Decimal
    currency: str
```

A **spend record** is the atomic unit. `query` aggregates these into `SpendBucket`s according to the requested granularity and grouping.

---

## 7. Error model

Errors are represented **in-band** for partial-success operations and as **exceptions** for programming mistakes or total failures.

### 7.1 In-band (sync and query)

`SyncResult.providers[].error` and `QueryResult.gaps` describe per-provider sync failures and missing or partial data ranges. Normal provider or data issues do not raise.

### 7.2 Exceptions

| Exception | When |
|-----------|------|
| `ConfigError` | Config missing, invalid YAML/schema (`load_config`, `ApiSpend` constructor). |
| `CredentialError` | Required env var for a configured provider is missing. |
| `StoreError` | Store cannot be opened or is unusable. |

All of the above inherit from `ApiSpendError`. Invalid arguments to helpers raise **`ValueError`** — programming errors, not the sync/query contract. Examples: **`run_query`** / **`ApiSpend.query`** with **`end <= start`**; **`configured_providers`** empty; **`providers`** containing a name not in **`configured_providers`**; **`sync(providers=[...])`** with a name not in the configured set.

---

## 8. Environment variables (complete list, v1)

### 8.1 Library and configured providers

| Variable | Required | Purpose |
|----------|----------|---------|
| `API_SPEND_CONFIG` | No | Override default config file path. |
| `API_SPEND_STORE_PATH` | No | Override default **store directory** (`~/.local/share/api-spend/`); DB file is `spend.sqlite` inside it (implementation). |
| `API_SPEND_OPENAI_API_KEY` | If provider configured | OpenAI **[Administrator API key](https://platform.openai.com/settings/organization/admin-keys)** (Costs API); not a default/project API key. See §3.1. |
| `API_SPEND_ANTHROPIC_API_KEY` | If provider configured | Anthropic admin API key (`sk-ant-admin…`). |
| `API_SPEND_BRIGHTDATA_API_KEY` | If provider configured | Bright Data account API token. |
| `API_SPEND_RESEND_API_KEY` | If provider configured | Resend API key. |
| `API_SPEND_BRAVE_API_KEY` | If provider configured | Brave Search API subscription key. |

### 8.2 Test-only and debugging (optional)

Not required for normal library use. **`API_SPEND_LIVE_TESTS=1`** (exactly `1`) enables live pytest modules. Copy-paste invocations: [`README.md`](README.md) **Live API tests**.

| Variable | When | Purpose |
|----------|------|---------|
| `API_SPEND_LIVE_TESTS` | Live pytest | Set to **`1`** to run (recommended). Some live modules also treat **`true`** / **`yes`** (case-insensitive) as enabled; others require exactly **`1`** — see per-module skip reasons if a run is skipped unexpectedly. |
| `API_SPEND_LIVE_DUMP_PATH` | Live pytest | After success, write JSON artifact to this path (shape: §8.3). |
| `API_SPEND_OPENAI_ORGANIZATION_ID` | `test_openai_live` only | Test harness org id; production uses YAML `options.organization_id`. |
| `API_SPEND_BRIGHTDATA_ZONE` | `test_brightdata_live` only | Test harness zone; production uses YAML `options.zone`. |
| `API_SPEND_RESEND_PLAN` | `test_resend_live` | `pro` or `free` (default `pro` in harness). |
| `API_SPEND_OPENAI_RAW_RESPONSE_PATH` | OpenAI adapter + live | Append JSON per HTTP response (see `http_raw_dump.py`). |
| `API_SPEND_ANTHROPIC_RAW_RESPONSE_PATH` | Anthropic adapter + live | Same pattern. |
| `API_SPEND_BRIGHTDATA_RAW_RESPONSE_PATH` | Bright Data adapter + live | Same pattern. |
| `API_SPEND_RESEND_RAW_RESPONSE_PATH` | Resend adapter + live | Same pattern. |
| `API_SPEND_BRAVE_RAW_RESPONSE_PATH` | Brave adapter + live | Same pattern. |

Raw capture target: file path, or `stdout` / `-` / `stderr`; appends with `---` separators. May contain secrets.

Full-stack live test: `tests/test_api_spend_live.py` uses **`API_SPEND_CONFIG`** plus keys from §8.1 for each provider in that YAML; store is pytest temp SQLite.

### 8.3 Live test JSON dump shapes (non-normative)

Documented so agents have one reference; pytest output is not part of the runtime API contract.

| Live test module | JSON payload (summary) |
|------------------|-------------------------|
| `tests/test_api_spend_live.py` | `validate`, `sync`, `query`, `status`, `providers` — `model_dump(mode="json")`. Snapshot rows: `sync.providers[].counter_observed`. |
| `tests/test_openai_live.py` | `range`, `record_count`, `records`. |
| `tests/test_anthropic_live.py` | Same as OpenAI. |
| `tests/test_brightdata_live.py` | Same as OpenAI. |
| `tests/test_resend_live.py` | `{"runs":[...]}` — `counter_observed`, `records` per run. |
| `tests/test_brave_live.py` | Same `runs` shape as Resend. |

---

## 9. Future versions (non-normative here)

**v2+** ideas and locked **`Vx-…`** rows live in [`BACKLOG.md`](BACKLOG.md) until promoted here (HTTP server mode, Google Cloud, budgets, usage metrics beyond cost, balances/credits, forecasting, tags, advanced store ops, etc.).

---

## 10. Changelog

Record breaking contract changes in release notes when you publish versions.
