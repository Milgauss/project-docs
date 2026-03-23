# Implementation checklist

**Agents:** [`README.md`](README.md) (agents + terminal blocks) → [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0 → §3+ → [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) → [`DECISIONS.md`](DECISIONS.md) → **this file**. Optional: [`BACKLOG.md`](BACKLOG.md), [`implementation-notes.md`](implementation-notes.md). **v1:** phases 1–9 below are `[x]`; use this file for any new checkpoints you add.

**vs `IMPLEMENTATION_PLAN.md`:** Only **this file** has `[ ]` / `[x]` checklists. The plan is architecture and phase **context** — not a second checklist. Link contract § and plan §; do not paste long specs here. Ordering: **TODO** = what to do next; plan = module layout unless `PLANNED_INTERFACE.md` overrides.

**Contract > plan.** Each checkpoint = implement, then test (phases = [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) section 4).

### Checkpoints: decisions *before* implementation

1. **`Refs: D-…`** → [`DECISIONS.md`](DECISIONS.md) **§2–§3** (shipped vs pending-ship). Do not paste full resolutions here.
2. **No `Refs:` yet** → follow **`PLANNED_INTERFACE.md`** + open **`BACKLOG.md`**; do not invent behavior until the interface is updated. After locking, add **`D-…`** and **`Refs:`**.

---

## Checkpoints (implement → test → …)

**Legend:** `[ ]` = not started · `[x]` = done. `Refs:` = `DECISIONS.md` sections 2–3. A **`[x]` on a phase or `N.x` heading** means every sub-bullet under that heading is `[x]`.

---

### [x] Phase 1 — Project scaffold, models, exceptions

#### [x] 1.1 Implement — Scaffold

**Refs:** `D-RELEASE-NAME`, `D-PYTHON-VERSION`

- [x] `pyproject.toml` with package name `api-spend`, Python 3.11+, dependencies (pydantic, httpx, pyyaml).
- [x] `src/api_spend/` package layout with `__init__.py`.
- [x] `exceptions.py`: `ApiSpendError`, `ConfigError`, `CredentialError`, `StoreError`.
- [x] `models.py`: all public Pydantic `BaseModel` types from `PLANNED_INTERFACE.md` §5–§6 (`SpendRecord`, `SpendBucket`, `QueryResult`, `GapInfo`, `SyncResult`, `ProviderSyncStatus`, `ProviderInfo`, `ProviderCapabilities`, `Status`, `ValidateResult`, `ProviderValidation`).

#### [x] 1.2 Test — Scaffold

- [x] `pip install -e .` succeeds.
- [x] `import api_spend` works; models and exceptions are importable.
- [x] Unit tests: construct each model with sample data; `.model_dump()` round-trips correctly.

---

### [x] Phase 2 — Config loading + validation

#### [x] 2.1 Implement — Config

**Refs:** `D-CONFIG-FORMAT`, `D-LOOKBACK`

- [x] `config.py`: Pydantic model for config shape (`sync.lookback_days`, `providers[]` with `name` and `options`).
- [x] YAML loader: reads from default path (`~/.config/api-spend/config.yaml`) or `API_SPEND_CONFIG` env var or explicit path.
- [x] Credential env vars: read each configured provider’s key from `os.environ` using the **explicit names in `PLANNED_INTERFACE.md` §8** (not a mechanical `API_SPEND_{name}_API_KEY` — e.g. `brave_search` → `API_SPEND_BRAVE_API_KEY`); central map in `config.py`.
- [x] Raises `ConfigError` on missing file, invalid YAML, or schema violations.
- [x] Raises `CredentialError` when a configured provider's required env var is missing.

#### [x] 2.2 Test — Config

- [x] Valid YAML config loads and validates; fields match expected values.
- [x] Missing config file raises `ConfigError`.
- [x] Malformed YAML raises `ConfigError`.
- [x] Unknown provider name in config raises `ConfigError`.
- [x] Missing env var for a configured provider raises `CredentialError`.
- [x] `API_SPEND_CONFIG` env var overrides default path.
- [x] `sync.lookback_days` defaults to 60 when omitted.

---

### [x] Phase 3 — SQLite store

#### [x] 3.1 Implement — Store

- [x] `store.py`: open or create SQLite database at configured path (or `:memory:` for tests).
- [x] Schema: `spend_records`, `sync_metadata`, `snapshots` tables per `IMPLEMENTATION_PLAN.md` §3.
- [x] Insert spend records with deduplication (`INSERT OR REPLACE`).
- [x] Query spend records by date range, optional provider filter.
- [x] Sync metadata CRUD: read/write `last_synced` and `latest_date` per provider.
- [x] Snapshot CRUD: insert snapshot, read latest snapshot per provider.
- [x] `reset()`: delete all records or per-provider; clear sync metadata and snapshots.
- [x] `StoreError` on open/create failure.

#### [x] 3.2 Test — Store

- [x] Insert records; query returns them with correct `Decimal` amounts.
- [x] Duplicate insert (same provider + service + date) replaces the old record.
- [x] Date-range query filters correctly (inclusive start, exclusive end).
- [x] Provider filter returns only matching records.
- [x] Sync metadata round-trips (write then read).
- [x] Snapshot insert + read latest returns most recent.
- [x] `reset()` clears all data; `reset(providers=["x"])` clears only that provider.
- [x] Store size query returns a reasonable byte count.

---

### [x] Phase 4 — Query engine

#### [x] 4.1 Implement — Query

**Refs:** `D-CURRENCY-V1`, `D-QUERY-BUCKETS-V1`

- [x] `query.py`: generate contiguous bucket boundaries for `[start, end)` given `granularity` (`"day"`, `"week"`, `"month"`).
- [x] Group records into buckets by `group_by` key(s) (`"provider"`, `"service"`, or both).
- [x] Fill missing buckets with zero-amount entries so output is contiguous.
- [x] Compute `coverage` per bucket: `"complete"`, `"partial"`, or `"estimated"` based on provider data presence and type.
- [x] Build `GapInfo` entries for provider × date-range holes.
- [x] Return `QueryResult` with `buckets`, `providers_included`, `gaps`.

#### [x] 4.2 Test — Query

- [x] Daily granularity: 7 days of fixture data → 7 contiguous buckets.
- [x] Weekly granularity: 14 days → 2 buckets; amounts aggregate correctly.
- [x] Monthly granularity: 3 months → 3 buckets.
- [x] `group_by="provider"`: separate bucket series per provider.
- [x] `group_by="service"`: separate bucket series per service.
- [x] `group_by=["provider", "service"]`: cross-dimensional grouping; `group` dict has both keys.
- [x] `group_by=None`: single total per bucket.
- [x] Missing data in a bucket → `coverage: "partial"` and corresponding `GapInfo`.
- [x] Estimated-only data → `coverage: "estimated"`.
- [x] Empty store → all-zero buckets, full gap coverage.
- [x] Provider filter restricts which providers appear in buckets and gaps.

---

### [x] Phase 5 — Provider framework + OpenAI adapter

#### [x] 5.1 Implement — Provider base + registry

**Refs:** `D-V1-PROVIDERS`, `D-BILLING-FETCH-V1`

- [x] `providers/base.py`: `BillingApiProvider` and `SnapshotProvider` abstract base classes.
- [x] `providers/__init__.py`: registry mapping provider name → class.

#### [x] 5.2 Implement — OpenAI adapter

**Refs:** `D-BILLING-FETCH-V1`

- [x] `providers/openai.py`: implements `BillingApiProvider`.
- [x] `fetch_costs(start, end)`: calls `GET /v1/organization/costs` with `start_time`/`end_time`, paginates, returns `FetchCostsResult` with normalized `SpendRecord`s.
- [x] `validate_credentials()`: lightweight API probe.
- [x] Maps OpenAI line items / models to `service` field (`options.organization_id` for `OpenAI-Organization`).

#### [x] 5.3 Test — OpenAI adapter

- [x] Mocked HTTP response → `fetch_costs` returns correctly normalized `SpendRecord` list.
- [x] Pagination: multi-page response handled correctly.
- [x] API error response → returns empty list + error (not exception).
- [x] `validate_credentials` with valid mock → `True`; invalid → `False`.

---

### [x] Phase 6 — Remaining billing-API adapters

#### [x] 6.1 Implement — Anthropic adapter

**Refs:** `D-V1-PROVIDERS`, `D-BILLING-FETCH-V1`

- [x] `providers/anthropic.py`: implements `BillingApiProvider`.
- [x] Calls `GET /v1/organizations/cost_report` with `starting_at`/`ending_at`, normalizes to `list[SpendRecord]`.
- [x] `validate_credentials()`: checks key format (`sk-ant-admin…`) + lightweight probe.

#### [x] 6.2 Test — Anthropic adapter

- [x] Mocked response → correctly normalized spend records.
- [x] Invalid key format → `validate_credentials` returns `False` without making a call.

#### [x] 6.3 Implement — Bright Data adapter

**Refs:** `D-V1-PROVIDERS`, `D-BILLING-FETCH-V1`

- [x] `providers/brightdata.py`: implements `BillingApiProvider`.
- [x] Calls `GET /zone/cost` with `from`/`to`, normalizes to `list[SpendRecord]`.
- [x] `validate_credentials()`: lightweight probe.

#### [x] 6.4 Test — Bright Data adapter

- [x] Mocked response → correctly normalized spend records.
- [x] Zone breakdown maps to `service` field.

---

### [x] Phase 7 — Snapshot-based adapters

#### [x] 7.1 Implement — Snapshot sync logic

**Refs:** `D-V1-PROVIDERS`

- [x] Implement in a **shared helper** (`snapshot_sync.py`) so Phase 7 tests can run **without** a finished `ApiSpend`; Phase 8 `client.sync` calls this helper for snapshot providers.
- [x] Read previous snapshot from store, call `read_counter()`, compute delta, call `estimate_cost(delta)`, store new snapshot + spend record.
- [x] First snapshot (no previous): record counter but produce no spend record (no delta to compute).
- [x] Missed sync: delta spans the full gap; single record with the accumulated amount.
- [x] `snapshots.quota_period` + `SnapshotProvider.sync_quota_period(recorded_at)` (Resend: month vs UTC day when only daily quota header exists).

#### [x] 7.2 Implement — Resend adapter

- [x] `providers/resend.py`: implements `SnapshotProvider`.
- [x] `read_counter()`: `GET /emails` (`limit=100`) with `Accept` + `User-Agent`; prefers `x-resend-monthly-quota`, then `x-resend-daily-quota`, then paginated list count in current UTC month when quota headers are omitted.
- [x] `estimate_cost(delta)`: multiplies by plan-specific per-email rate from config `options.plan`.
- [x] `validate_credentials()`: lightweight probe.

#### [x] 7.3 Test — Resend adapter

- [x] Mocked response with header → `read_counter()` returns correct value.
- [x] `estimate_cost` math: 100 emails × $0.0004 = $0.04.
- [x] Full snapshot cycle: first sync records counter only; second sync produces a spend record with correct delta.

#### [x] 7.4 Implement — Brave Search adapter

- [x] `providers/brave.py`: implements `SnapshotProvider`.
- [x] `read_counter()`: cheapest `web/search` probe; parses comma-separated `X-RateLimit-Limit` / `X-RateLimit-Remaining` (paired segments), picks window via `X-RateLimit-Policy` `w=` or largest positive limit; returns used = limit - remaining for that segment.
- [x] `estimate_cost(delta)`: multiplies by $5/1000 requests.
- [x] `validate_credentials()`: lightweight probe.

#### [x] 7.5 Test — Brave Search adapter

- [x] Mocked response with rate-limit headers → `read_counter()` returns correct usage.
- [x] `estimate_cost` math: 500 requests × $0.005 = $2.50.
- [x] Full snapshot cycle: delta between two snapshots produces correct spend record.

---

### [x] Phase 8 — Facade wiring + integration tests

#### [x] 8.1 Implement — `ApiSpend` client

**Refs:** `D-FACADE-INIT-V1`, `D-BILLING-SYNC-WINDOW-V1`, `D-PROVIDER-CAPS-V1`

- [x] `client.py`: `ApiSpend` class — constructor wires config (`load_config` + optional **`require_credentials`**, optional injected **`SpendStore`** per **`PLANNED_INTERFACE.md`** section 4.3), default store path when not injected, and provider registry.
- [x] `sync()`: iterates providers, calls billing-API or snapshot logic, writes to store, returns `SyncResult` with partial-success semantics.
- [x] `query()`: delegates to query engine, returns `QueryResult`.
- [x] `providers()`: returns `list[ProviderInfo]` from config + store metadata + static capabilities.
- [x] `status()`: returns `Status` from store metadata.
- [x] `validate()`: checks config + credentials + optional connectivity probe, returns `ValidateResult`.
- [x] `reset()`: delegates to store, returns nothing.
- [x] `__init__.py`: re-export `ApiSpend` alongside existing public surface (models, exceptions, `run_query`, store, config helpers).

#### [x] 8.2 Test — Integration

**Refs:** `D-FACADE-INIT-V1`, `D-BILLING-SYNC-WINDOW-V1`, `D-PROVIDER-CAPS-V1`

- [x] Full lifecycle: construct `ApiSpend` with test config → `validate()` → `sync()` → `query()` → assert bucket shapes match contract.
- [x] `validate()`: default `check_connectivity` → every `ProviderValidation.reachable` is `None`; config/credentials flags still set correctly.
- [x] `validate(check_connectivity=True)` with mocked HTTP → `reachable` is `True` or `False` per provider as probes succeed or fail (`PLANNED_INTERFACE.md` section 5.5).
- [x] Partial sync failure: one provider errors, others succeed; `SyncResult` reflects both.
- [x] `providers()` returns correct capabilities and sync timestamps after sync.
- [x] `status()` reflects correct counts and last sync time.
- [x] `reset()` clears data; subsequent `query()` returns zero-amount buckets.
- [x] `reset(providers=["openai"])` clears only OpenAI; other providers' data remains.
- [x] `group_by=["provider", "service"]` end-to-end: sync two providers → query → buckets have correct cross-dimensional groups.
- [x] **Live (opt-in):** `tests/test_api_spend_live.py` — with **`API_SPEND_LIVE_TESTS=1`**, **`API_SPEND_CONFIG`** pointing at a YAML that lists each provider to exercise, and the usual credential env vars (and YAML **`options`** such as OpenAI **`organization_id`**, Bright Data **`zone`**) for those providers, construct **`ApiSpend`**, run **`validate()`** (e.g. `check_connectivity=False` or as documented), **`sync()`** for all configured providers, then **`query()`** and assert contract-shaped results (including tolerating partial failure if one provider errors). Prefer a **throwaway store** (**`API_SPEND_STORE_PATH`** or temp dir) so the default **`spend.sqlite`** is not touched. Skip the module (or individual providers) when required secrets for that provider are missing — same pattern as per-provider live tests. Document in [README](README.md).

---

### [x] Phase 9 — Hardening

#### [x] 9.1 Implement — Polish

**Refs:** `D-LOGGING-V1`

- [x] Structured logging via stdlib `logging` per **`PLANNED_INTERFACE.md` §4.4`: hierarchy under **`api_spend`**; **INFO** / **DEBUG** as there; **caller-configured** handlers/levels (no library env var in **§8**); never log secrets.
- [x] Edge case handling: empty store queries; **zero configured providers** — contract **§4.2** / **§5.1** / **§5.2** / **§7.2** (**`query`** → **`ValueError`**; **`sync`** empty list); all providers failing sync (in-band **`SyncResult`** only).
- [x] README: agent-first entry, **`cd /path/to/api-spend`** in live-test examples, **`ApiSpend`** minimal sample (see §4.3 for options).
- [x] `PLANNED_INTERFACE.md`: §5 intro states shipped **`ApiSpend`** + lower-level helpers (recheck if “planned” wording reappears).
- [x] When adapters, `api_spend.__init__` exports, or live-test/debug env behavior change: reconcile **`PLANNED_INTERFACE.md` §8** (§8.1–§8.3), **`README.md`** live commands (copy-paste only per §0), **`schemas/public_pydantic_schemas.json`** (run **`python scripts/export_public_schema.py`** if any public **`BaseModel`** changed), and **`.gitignore`** in one pass.
- [x] **Quarterly or each release:** [`BACKLOG.md`](BACKLOG.md) hygiene — [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §7 (fold shipped items; open bullets must not duplicate v1 contract prose).

#### [x] 9.2 Test — Contract alignment

- [x] All public model fields match `PLANNED_INTERFACE.md` sections 5–6 (field names, types, semantics).
- [x] All env vars in **`PLANNED_INTERFACE.md` §8** are documented and functional; §8.2/§8.3 match code and live tests; **`README.md`** keeps examples only (§0).
- [x] All exceptions from `PLANNED_INTERFACE.md` section 7 are raised in the documented circumstances.
- [x] Query with no synced data returns contiguous zero-amount buckets with `coverage: "partial"` and full gap list.

---

*Ship a `D-…`? Move it from `DECISIONS.md` section 3 → section 2.*
