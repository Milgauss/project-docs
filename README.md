# API Spend

Python library: sync API spend into SQLite; time-bucketed **USD** `query` for dashboards. Billing APIs and snapshot **estimates** both use `SpendRecord`.

**Status:** v1 complete (Phases 1–9). Facade: `ApiSpend` in `src/api_spend/client.py`. [`DECISIONS.md`](DECISIONS.md) · [`BACKLOG.md`](BACKLOG.md) · [`TODO.md`](TODO.md).

---

## For coding agents

Read in order; contract wins on conflict.

| Step | Action |
|------|--------|
| **SoT** | [`PLANNED_INTERFACE.md` §0](PLANNED_INTERFACE.md#sources-of-truth) — norms, models, errors, **§8** env names. Do not paste API semantics into this README. |
| **Order** | `PLANNED_INTERFACE.md` > `IMPLEMENTATION_PLAN.md` > code. |
| **cwd** | Directory must contain `pyproject.toml` and `tests/`. Wrong cwd → `pytest` “file or directory not found: tests/”. |
| **Task path** | `PLANNED_INTERFACE.md` → `IMPLEMENTATION_PLAN.md` → [`TODO.md`](TODO.md) → [`DECISIONS.md`](DECISIONS.md) §2–§3 if `Refs: D-…` → optional [`implementation-notes.md`](implementation-notes.md), [`BACKLOG.md`](BACKLOG.md). |
| **Verify** | Use **Bootstrap** and **Default test run** blocks below (always `cd` first). |
| **After edits** | [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) — public-surface checklist, post-change ritual, schema regen. |

**Hot paths:** `src/api_spend/client.py` (`ApiSpend`), `config.py`, `store.py`, `query.py`, `snapshot_sync.py`, `providers/*.py`, `providers/__init__.py` (`PROVIDER_REGISTRY`).

**Tests (roles):** `tests/test_client.py` (mocked facade), `tests/test_phase9_contract.py` (models, §8 env set, exceptions, empty store), `tests/test_doc_drift.py` + `tests/test_public_schema_snapshot.py` (README/plan strings + JSON Schema snapshot), `tests/test_api_spend_live.py` + `tests/test_*_live.py` (opt-in HTTP).

**Semantics:** `query` = USD from **stored** rows. `sync` → `ProviderSyncStatus.counter_observed` = snapshot counter **at that sync** (Resend/Brave), not inside `query`. See `PLANNED_INTERFACE.md` §5.1, §5.2, §3.2.

**Logging:** `PLANNED_INTERFACE.md` §4.4 — loggers `api_spend.*`; you attach handlers/levels; no `API_SPEND_*` log-level env in §8.

---

## Documentation index

| Doc | Role |
|-----|------|
| [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) | Contract: §0 SoT, §3–§7, §8 env, §5–§6 models |
| [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) | Modules, stack §2, phases §4 |
| [`TODO.md`](TODO.md) | Checklist; `Refs: D-…` |
| [`DECISIONS.md`](DECISIONS.md) | `D-…` §2 shipped / §3 pending |
| [`BACKLOG.md`](BACKLOG.md) | `Vx-…`, v2+ (not contract) |
| [`config.example.yaml`](config.example.yaml) | Example YAML; rules in contract §3–§4, §8 |
| [`implementation-notes.md`](implementation-notes.md) | Retros; not normative |
| [`COLLABORATION_AND_AI_RULES.md`](COLLABORATION_AND_AI_RULES.md) | Process, §6 lessons, drift checklist |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history; semver and contract alignment |
| [`schemas/public_pydantic_schemas.json`](schemas/public_pydantic_schemas.json) | CI snapshot of public models; regen script below |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | CI: Python 3.11 + 3.12, `pytest` |

Optional: [`FRAMEWORKS.md`](FRAMEWORKS.md) — tool catalog for adjacent work; not SoT ([`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2). [`ai-prompt-examples.md`](ai-prompt-examples.md) — may be `.cursorignore`’d.

---

## Stack

Python 3.11+ · Pydantic v2 · httpx · PyYAML · SQLite. Detail: [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §2.

**SQLite:** the default store is a **local SQLite file**. Treat it as a **single-writer** store from the library’s perspective; multiple concurrent writers (or separate processes writing the same file without your own coordination) can corrupt the database or cause locking errors. For dashboards, prefer one sync job or process owning the store, or use your own replication strategy.

---

## For dashboard integrators (Python or Node)

This package is **Python-only**. **Python** apps can `import api_spend` and call **`ApiSpend`** directly.

**Node-only** stacks cannot import this library natively. Integrate via a **Python sidecar** (small service), a **scheduled job** that refreshes the SQLite file or exports JSON your Node app reads, or **`subprocess`** to a Python CLI you wrap—whatever matches your deployment; the integration boundary is not “npm install api-spend”.

**Private install** (no PyPI required): install from **git** or from a **vendored copy** of this repo.

```bash
# Example: pinned tag (replace URL and credentials as needed)
pip install "git+https://github.com/your-org/api-spend.git@v1.0.0"

# Or: submodule / monorepo checkout at ./vendor/api-spend
pip install -e ./vendor/api-spend
```

Same **`API_SPEND_*`** env and YAML rules as in [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §8 and [`config.example.yaml`](config.example.yaml).

---

## Bootstrap (from clone)

Run from your machine; replace `/path/to/api-spend` with the repo root (folder containing `pyproject.toml`).

```bash
cd /path/to/api-spend
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Editable install without dev deps: `pip install -e .` (same `cd` + venv).

---

## Default test run

```bash
cd /path/to/api-spend
source .venv/bin/activate
pytest
```

Fast checks only:

```bash
cd /path/to/api-spend
source .venv/bin/activate
pytest -q tests/test_doc_drift.py tests/test_public_schema_snapshot.py
```

Live modules need `API_SPEND_LIVE_TESTS=1` (see **Live API tests**). Print skip reasons: `pytest -v -rs …`.

---

## Regenerate public JSON Schema snapshot

After changing any public `BaseModel` type exported in `api_spend.__all__` (the schema script only serializes subclasses of `BaseModel`):

```bash
cd /path/to/api-spend
source .venv/bin/activate
python scripts/export_public_schema.py
pytest -q tests/test_public_schema_snapshot.py
```

Commit `schemas/public_pydantic_schemas.json` with the code change.

---

## ApiSpend (minimal)

```python
from datetime import date
from api_spend import ApiSpend

with ApiSpend() as client:
    client.sync()
    result = client.query(date(2025, 1, 1), date(2025, 2, 1), granularity="day")
```

Options (injected `SpendStore`, `require_credentials`, `http_client`): `PLANNED_INTERFACE.md` §4.3. Config path: arg → `API_SPEND_CONFIG` → `~/.config/api-spend/config.yaml`. Store dir: `API_SPEND_STORE_PATH` or default (§8).

---

## Live API tests (optional)

Real HTTP; charges may apply. Variable **names** and dump shapes: `PLANNED_INTERFACE.md` **§8.2**, **§8.3**. This section is **commands only** — not a second spec.

**Gate:** `export API_SPEND_LIVE_TESTS=1` (use `1`; some modules also accept `true` / `yes` — see §8.2).

**First time:** run **Bootstrap** above so `pytest` and deps exist.

**Every run:** each block below is self-contained (`cd` + venv + exports + `pytest`).

### Full-stack (`ApiSpend`)

`tests/test_api_spend_live.py` — needs `API_SPEND_CONFIG` pointing at YAML that lists providers to test; export each `API_SPEND_*_API_KEY` for those names. Pytest uses a **temp** SQLite DB.

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_CONFIG=/path/to/api-spend/config.yaml
# export API_SPEND_OPENAI_API_KEY='...'
# export API_SPEND_ANTHROPIC_API_KEY='...'
# … one key per provider in the YAML …
# optional:
# export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/api_spend_full_stack_live.json
pytest tests/test_api_spend_live.py -v
# pytest tests/test_api_spend_live.py -v -rs   # show skip reasons
```

### OpenAI

[Costs API](https://platform.openai.com/docs/api-reference/organization-costs) · [Admin key](https://platform.openai.com/settings/organization/admin-keys). Harness: `API_SPEND_OPENAI_ORGANIZATION_ID` (production uses YAML `options.organization_id`).

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_OPENAI_API_KEY='sk-...'
export API_SPEND_OPENAI_ORGANIZATION_ID='org-...'
pytest tests/test_openai_live.py -v
```

With dump + raw capture:

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_OPENAI_API_KEY='sk-...'
export API_SPEND_OPENAI_ORGANIZATION_ID='org-...'
export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/openai_live_costs.json
export API_SPEND_OPENAI_RAW_RESPONSE_PATH=/path/to/api-spend/openai_raw_response.json
pytest tests/test_openai_live.py -v
```

### Anthropic

[`GET /v1/organizations/cost_report`](https://docs.anthropic.com/en/api/admin-api/usage-cost/get-cost-report) — `sk-ant-admin…` only (`PLANNED_INTERFACE.md` §3.1).

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_ANTHROPIC_API_KEY='sk-ant-admin-...'
pytest tests/test_anthropic_live.py -v
```

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_ANTHROPIC_API_KEY='sk-ant-admin-...'
export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/anthropic_live_costs.json
pytest tests/test_anthropic_live.py -v
```

### Bright Data

[`GET …/zone/cost`](https://docs.brightdata.com/api-reference/account-management-api/Get_the_total_cost_and_bandwidth_stats_for_a_Zone). Harness: `API_SPEND_BRIGHTDATA_ZONE` (= YAML `options.zone`).

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_BRIGHTDATA_API_KEY='...'
export API_SPEND_BRIGHTDATA_ZONE='your_zone_name'
pytest tests/test_brightdata_live.py -v
```

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_BRIGHTDATA_API_KEY='...'
export API_SPEND_BRIGHTDATA_ZONE='your_zone_name'
export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/brightdata_live_costs.json
pytest tests/test_brightdata_live.py -v
```

### Resend

[List emails](https://resend.com/docs/api-reference/emails/list-emails) — §3.2. Optional `API_SPEND_RESEND_PLAN`: `pro` | `free`.

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_RESEND_API_KEY='re_...'
export API_SPEND_RESEND_PLAN='pro'
pytest tests/test_resend_live.py -v
```

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_RESEND_API_KEY='re_...'
export API_SPEND_RESEND_PLAN='pro'
export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/resend_live_snapshot.json
export API_SPEND_RESEND_RAW_RESPONSE_PATH=/path/to/api-spend/resend_raw_response.json
pytest tests/test_resend_live.py -v
```

### Brave Search

[Web Search](https://api.search.brave.com/app/documentation/web-search/query) — `X-Subscription-Token`. §3.2.

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_BRAVE_API_KEY='BSA...'
pytest tests/test_brave_live.py -v
```

```bash
cd /path/to/api-spend
source .venv/bin/activate
export API_SPEND_LIVE_TESTS=1
export API_SPEND_BRAVE_API_KEY='BSA...'
export API_SPEND_LIVE_DUMP_PATH=/path/to/api-spend/brave_live_snapshot.json
export API_SPEND_BRAVE_RAW_RESPONSE_PATH=/path/to/api-spend/brave_raw_response.json
pytest tests/test_brave_live.py -v
```

### Raw HTTP debug (example)

§8.2: `API_SPEND_*_RAW_RESPONSE_PATH`. Code: `src/api_spend/http_raw_dump.py`.

```bash
cd /path/to/api-spend
source .venv/bin/activate
rm -f ./openai_raw_response.json
export API_SPEND_LIVE_TESTS=1
export API_SPEND_OPENAI_API_KEY='...'
export API_SPEND_OPENAI_ORGANIZATION_ID='org-...'
export API_SPEND_OPENAI_RAW_RESPONSE_PATH=/path/to/api-spend/openai_raw_response.json
pytest tests/test_openai_live.py -v
```

### Live dump fixtures (sanitized regression)

```bash
cd /path/to/api-spend
source .venv/bin/activate
pytest tests/test_live_cost_dump_fixtures.py
```

---

## Public imports (reference)

Authoritative list: `api_spend.__all__` in `src/api_spend/__init__.py`. Example:

```python
from api_spend import (
    ApiSpend,
    SpendRecord,
    SpendStore,
    load_config,
    run_query,
    run_snapshot_sync,
)
```

Lower-level: `SpendStore.open`, `load_config`, `run_query(..., configured_providers=…)` — `PLANNED_INTERFACE.md` §4.2, §5.2.

---

## License

Released under the [MIT License](LICENSE). See [`CHANGELOG.md`](CHANGELOG.md) for release notes.
