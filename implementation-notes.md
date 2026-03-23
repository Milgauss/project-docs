# Implementation notes

Informal retros per [`TODO.md`](TODO.md) phase — **not** normative. **Agents:** skip unless debugging history; never substitute [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §0. Commands / cwd: [`README.md`](README.md). Active work: [`TODO.md`](TODO.md).

**Policy:** Do **not** add new normative requirements here. Older **Phase N** blocks stay for **record keeping** only; if a retro disagrees with the contract, **the contract wins**. When capturing new lessons, prefer **`COLLABORATION_AND_AI_RULES.md`** §6 or a short addendum that **links** **`PLANNED_INTERFACE.md`** instead of duplicating field-level rules.

**Maintenance (pruning):** There is **no** calendar rule like “delete everything before Phase *N*.” **When to edit this file:**

1. **On each release** or when you touch code/docs that a phase retro references, re-read that phase: **remove or one-line** bullets that are **obsolete**, wrong, or already stated in **`PLANNED_INTERFACE.md`**, **`DECISIONS.md`**, tests, or **[`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §6**.
2. **Compress** long, stable sections: replace many bullets with a short summary + links to **`src/`** / **`tests/`**; **keep the `### Phase …` heading** so history stays grep-friendly.
3. **Promote first, then prune:** move enduring lessons into [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §6, then shorten the phase note to “folded into §6 — *topic*” or delete the duplicate bullets.
4. **Do not** delete the *only* explanation of a non-obvious behavior until that behavior lives in the **contract**, **COLLABORATION §6**, or **`DECISIONS.md`**.

**Phase index** (deep detail lives under each heading below):

| Phase | Topic | Primary code / tests |
|-------|--------|----------------------|
| 1 | Scaffold, models, exceptions | `models.py`, `exceptions.py`, `test_models.py` |
| 2 | Config YAML, credentials | `config.py`, `test_config.py` |
| 3 | SQLite store | `store.py`, `test_store.py` |
| 4 | Query / buckets / gaps | `query.py`, `test_query.py` |
| 5 | Billing framework, OpenAI | `providers/openai.py`, `test_openai.py` |
| 6 | Anthropic, Bright Data billing | `providers/anthropic.py`, `brightdata.py`, tests |
| 7 | Resend, Brave snapshots | `providers/resend.py`, `brave.py`, `snapshot_sync.py` |
| 8 | `ApiSpend` facade | `client.py`, `test_client.py`, `test_api_spend_live.py` |
| 9 | Logging, contract tests | `client.py`, `store.py`, `config.py`, `test_phase9_contract.py` |

---

### Phase 1 — Project scaffold, models, exceptions

**Post-implementation review** (after **1.1 Implement — Scaffold** and **1.2 Test — Scaffold**).

*Shipped per [`TODO.md`](TODO.md); **`D-RELEASE-NAME`**, **`D-PYTHON-VERSION`** in [`DECISIONS.md`](DECISIONS.md). Stack: Pydantic v2, `pyproject.toml` + `src/`, models §5–§6.*

**Friction / watch-outs**

1. **PEP 668** — use a **`.venv`** (folded into [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) §6).
2. **README** leads with **For coding agents** (precedence, cwd, tests, hot paths); live tests use explicit **`cd /path/to/api-spend`** blocks.
3. **`SpendBucket.coverage`** is a **`Literal[...]`** in code while the contract says `str` — stricter validation; JSON output is still plain strings.
4. **`frozen=True`** on public **`BaseModel`**s is an implementation choice (immutable value objects), not spelled out in the contract.

**No major blockers.**

---

### Phase 2 — Config loading + validation

**Post-implementation review** (after **2.1 Implement — Config** and **2.2 Test — Config**).

*Shipped; **`D-CONFIG-FORMAT`**, **`D-LOOKBACK`** in [`DECISIONS.md`](DECISIONS.md) §2. Path order: explicit → `API_SPEND_CONFIG` → default.*

**Friction / watch-outs**

1. **Credential env vars** — explicit `provider → env` map (e.g. **`brave_search` → `API_SPEND_BRAVE_API_KEY`**); see COLLABORATION §6 **Credential env names** and [`src/api_spend/config.py`](src/api_spend/config.py).
2. **`pydantic.ValidationError`** → **`ConfigError`** at the boundary (COLLABORATION §6 **Public errors vs Pydantic**; [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §7).
3. **YAML edge cases:** `safe_load` of an empty file → **`None`** (normalize to `{}`); top-level **non-dict** needs an explicit error.
4. **`load_config(..., require_credentials=False)`** is for **tests** and YAML-only checks; **`ApiSpend`** defaults to **`require_credentials=True`** per **`PLANNED_INTERFACE.md`** §4.3 and **`D-FACADE-INIT-V1`**.

**No major blockers.**

---

### Phase 3 — SQLite store

**Post-implementation review** (after 3.1 / 3.2 shipped).

*Shipped; schema in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §3. COLLABORATION §6 **SQLite store path** covers mkdir, approximate size, UTC ISO datetimes.*

**Friction / watch-outs** (phase-specific)

1. **`approximate_size_bytes()`** vs **`os.path.getsize()`** when WAL / `-wal` / `-shm` exist — logical SQLite size only.
2. **Snapshot `ORDER BY recorded_at`** assumes consistent ISO formatting from one write path.
3. **Per-method `commit()`** — possible future: one transaction around **`ApiSpend.sync`**.
4. **`StoreError`:** opening a **directory** as DB path is a portable negative test.

---

### Phase 4 — Query engine

**Post-implementation review** (after **4.1 Implement — Query** and **4.2 Test — Query**).

*Shipped; **`D-CURRENCY-V1`**, **`D-QUERY-BUCKETS-V1`**. **`configured_providers`** scopes gaps; **`SNAPSHOT_PROVIDERS`** drives **`estimated`** coverage.*

**Friction / watch-outs**

1. **Pydantic v2** — keyword args on public models (COLLABORATION §6 **Pydantic v2 `BaseModel` constructors**).
2. **`run_query`**, **`iter_bucket_periods`**, **`V1_QUERY_CURRENCY`** re-exported for callers with an existing **`SpendStore`**.

---

### Phase 5 — Provider framework + OpenAI adapter

**Post-implementation review** (after **5.1**–**5.3**).

*Shipped; **`D-BILLING-FETCH-V1`**, **`FetchCostsResult`**. OpenAI: **`openai_options_from_config`** for YAML **`organization_id`**. COLLABORATION §6 **Mocking `httpx`**.*

**Friction / watch-outs**

1. Re-validate cost **`group_by`** against live OpenAI if the API changes.
2. **`validate_credentials`** uses the Costs API — requires an **admin**-capable key.

---

### Phase 6 — Anthropic + Bright Data billing adapters

**Post-implementation review** (after **6.1**–**6.4**).

*Shipped; **`D-V1-PROVIDERS`**. Normative adapter rules: **`PLANNED_INTERFACE.md`** §3.1 (Anthropic minor units, **`sk-ant-admin`**, Bright Data **`back_dN`/`back_mN`/`custom`**, merge order). COLLABORATION §6 **Billing adapters**.*

**Friction / watch-outs**

1. Anthropic **`group_by`** vs live **`cost_report`** docs.
2. Bright Data **`_parse_zone_cost_payload`** — vendor anchor changes need code + tests together.

---

### Phase 7 — Snapshot adapters (Resend, Brave Search)

Contract + behavior: **`PLANNED_INTERFACE.md`** section 3.2; code: **`src/api_spend/providers/resend.py`**, **`src/api_spend/providers/brave.py`**, **`src/api_spend/snapshot_sync.py`**.

**Resend (live gotcha):** **`GET /emails`** may omit **`x-resend-*-quota`** and only return **`ratelimit-*`** — that is **request** throttling, not send quota. Fallback = paginated list count in **current UTC month** (newest-first assumption, **`~0.21s`** between pages). List totals may not match vendor quota rules (e.g. non-listed mail).

**Brave (live gotcha):** **`X-RateLimit-Limit` / `Remaining`** can be **comma-separated** paired windows; pick segment via **`X-RateLimit-Policy`** **`w=`** (longest among **`limit > 0`**) or else **largest** positive limit. A **second** sync in one live test often shows **+1** request because the first probe call consumes quota.

**Dumps:** **`http_raw_dump`** usually stores **JSON bodies**, not headers — extend the dumper or rely on pytest output when debugging rate-limit vs quota headers.

---

### Phase 8 — `ApiSpend` facade + integration tests

**Post-implementation review** (after **8.1 Implement — `ApiSpend` client** and **8.2 Test — Integration**).

**Code map:** [`src/api_spend/client.py`](src/api_spend/client.py), [`tests/test_client.py`](tests/test_client.py), [`tests/test_api_spend_live.py`](tests/test_api_spend_live.py).

*Shipped; **`D-FACADE-INIT-V1`**, **`D-BILLING-SYNC-WINDOW-V1`**, **`D-PROVIDER-CAPS-V1`**. Thin facade over **`load_config`**, **`run_query`**, **`run_snapshot_sync`**. COLLABORATION §6 **Integration tests** (injected **`http_client`**, close lifecycle). **`http_client=`** / **`D-FACADE-INIT-V1`**: [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §4.3.*

**Friction / watch-outs**

1. **`:memory:`** → **`Status.store_size_bytes`** is **`None`** (see Phase 3 / COLLABORATION §6 SQLite size).
2. **Billing window `start >= end`:** still update **`sync_metadata`**, **`records_added == 0`**, do **not** call **`fetch_costs`**.
3. **`provider_spend_date_bounds`** for **`ProviderInfo`** — keep aligned with query/gap semantics if schema changes.
4. **Mock anchor:** **`date.today() - 1 day`** inside lookback — rare UTC midnight flake.
5. **Live full-stack:** complete YAML **`options`** + keys per provider or skips.

---

### Phase 9 — Hardening (logging + contract alignment)

**Post-implementation review** (9.1 Polish + 9.2 Test — Contract alignment).

*Shipped; **`D-LOGGING-V1`** (COLLABORATION §6 **Library logging**). **`ApiSpend.query`** + empty YAML **`providers`**. **`tests/test_phase9_contract.py`** + **`tests/test_public_schema_snapshot.py`** for drift.*

**Friction / watch-outs**

1. **`config.py`:** define module **`logger`** before **`logger.debug`** in **`load_config`**.
2. **`API_SPEND_LIVE_TESTS`:** **`1`** vs **`true`/`yes`** — see **`PLANNED_INTERFACE.md`** §8.2.
3. **`SpendStore.reset`:** falsy **`providers`** (including **`[]`**) clears **all**; **`ApiSpend.reset()`** uses **`None`** only.

---

### Bright Data — live empty dump while dashboard showed usage

**Cause:** **`/zone/cost`** often returns **monthly** **`back_m*`** with real **`cost`**, while **daily** **`back_d*`** is missing or all zeros. The adapter originally read only **`back_dN`**, so **`record_count`** was **0**.

**Fix:** Parse **`back_mN`**, attribute to the **first day** of each month that intersects **`[start, end)`**, and prefer **daily** output whenever any daily cost is non-zero; otherwise use **monthly** rows. See **`tests/test_brightdata_monthly.py`**.

**Raw response:** Shared **`http_raw_dump.maybe_dump_http_response`** — per-provider env **`API_SPEND_OPENAI_RAW_RESPONSE_PATH`**, **`API_SPEND_ANTHROPIC_RAW_RESPONSE_PATH`**, **`API_SPEND_BRIGHTDATA_RAW_RESPONSE_PATH`** (see README).

**``custom`` bucket:** Some zones (e.g. web unlocker) return **`{ "<id>": { "custom": { "cost", "range": { "from", "to" } } } }`** with **no** **`back_d*`** / **`back_m*`** — parse **`custom`** into **`{zone}:custom`** (see **`tests/test_brightdata_custom.py`**).

---
