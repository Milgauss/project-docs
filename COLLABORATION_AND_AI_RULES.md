# Collaboration: human + AI

Process and tooling for human + AI collaboration (reusable as a template). Product truth: `PLANNED_INTERFACE.md` and the registers below.

---

## 1. Process

**Truth order:** `PLANNED_INTERFACE.md` overrides `IMPLEMENTATION_PLAN.md` and informal code assumptions.

**Agents (default doc pass):** [`README.md`](README.md) **For coding agents** + **Documentation index** → `PLANNED_INTERFACE.md` (**§0** SoT, then task sections) → `TODO.md` (checklist; v1 phases 1–9 are complete) → `DECISIONS.md` §2–§3 for **`Refs: D-…`**. `implementation-notes.md` = retros only (non-normative).

**Registers**

| Doc | Role |
|-----|------|
| `DECISIONS.md` | v1 **`D-…`**: section 2 shipped · section 3 locked (implementation may lag) · section 4 open. |
| `TODO.md` | Ordered v1 work; **`Refs: D-…`** where a decision row exists. |
| `BACKLOG.md` | **`Vx-…`** and v2+ ideas; promote into `PLANNED_INTERFACE.md` before treating as contract. Not **`D-…`** until folded into v1. |

**Execution (AI):** Run install/tests yourself; iterate on failures. Well-scoped work does not need step-by-step approval.

**Doc drift (PR / same change set):** If you change **public** behavior, models, or env vars: update **`PLANNED_INTERFACE.md`** first (§5–§6 fields, §8 names, §3–§5 semantics). Then **`README.md`** only if commands or discovery paths change — do **not** restate contract prose there (**§0** SoT). Grep **`README.md`** / **`IMPLEMENTATION_PLAN.md`** for old field or env names. **Automated:** **`tests/test_doc_drift.py`** (stale export wording, §0 anchor); **`tests/test_public_schema_snapshot.py`** vs **`schemas/public_pydantic_schemas.json`** — regenerate with **`python scripts/export_public_schema.py`** when public **`BaseModel`** shapes change.

**Public surface change checklist**

1. **`PLANNED_INTERFACE.md`** — behavior, models, errors, **§8** env names (link § anchors from other docs).
2. **`README.md`** — only if install commands, cwd, or discovery paths change; never paste new normative rules there (**§0**).
3. **`src/api_spend/__init__.py`** — **`__all__`** and re-exports match the intended public API.
4. **Schema snapshot** — if any public **`BaseModel`** in **`__all__`** changed: run **`python scripts/export_public_schema.py`** and commit **`schemas/public_pydantic_schemas.json`**.
5. **`DECISIONS.md` / `TODO.md`** — new or moved **`D-…`** / **`Refs:`** when behavior was decision-gated.

**Post-change ritual:** `cd` to repo root (dir with `pyproject.toml`), venv on, then **`pytest`**. Rename grep: `cd /path/to/api-spend` then **`rg OLD_TOKEN --glob '*.md' --glob '*.yaml' src/ tests/`**. PRs: **CI** `.github/workflows/ci.yml` (Python 3.11 + 3.12).

**Code:** Minimal diffs; match local style; reuse helpers instead of parallel implementations.

**Explanations:** Prefer **code citations** (`startLine:endLine:path`) for existing code; clear prose; read the **thread** for intent (refinement vs new ask).

---

## 2. Cursor rules (this workspace)

Under [`.cursor/rules/`](.cursor/rules/):

| File | Purpose |
|------|---------|
| [`.cursorrules`](.cursor/rules/.cursorrules) | Complex work → short plan first; simple → implement; keep functions small; prefer evidence before guessing fixes. |
| [`implementation-decisions.mdc`](.cursor/rules/implementation-decisions.mdc) | Before code: v1 ↔ `TODO` / `DECISIONS`; undecided behavior ↔ `BACKLOG` + interface update; future majors ↔ `Vx-…` then contract. |
| [`markdown-agent-priority.mdc`](.cursor/rules/markdown-agent-priority.mdc) | When editing **`*.md`**: prefer agent-oriented structure (§0 SoT, links not duplicate prose, terminal blocks). |

**New repo:** Copy `.cursor/rules/`, fix paths, adjust `globs` / `alwaysApply` on `.mdc` files.

---

## 3. User-level rules (optional)

Often set as **global Cursor user rules**. Themes: run commands and fix issues yourself; **markdown links** for web refs; **code blocks** for repo code; never log or echo **secrets**.

---

## 4. Bootstrap checklist (new project)

1. One contract doc (API, formats, errors).
2. `DECISIONS.md` + `TODO.md` with `Refs: D-…` where locked.
3. `BACKLOG.md` with `Vx-…` + v2+ ideas.
4. Cursor rules that point at the above.
5. Runnable tests; README; `.env.example` / validate flow if env-gated.

---

## 5. Applying this template to your repo

**This repo:** dist **`api-spend`**, import **`api_spend`**, product **API Spend** (v1 = Python library). Keep names aligned in packaging and docs. Grow `PLANNED_INTERFACE.md` before `TODO.md`; one **`D-…`** row per real fork in `DECISIONS.md`.

---

## 6. Lessons learned

Short, actionable; prune when stale. Append when something pays off or burns you; copy or trim when starting a sibling project. When **`implementation-notes.md`** phase retros get long, **promote** enduring bullets here first, then compress or delete the duplicate phase text (see **§7** — **`implementation-notes` hygiene**).

- **Vocabulary:** Match the contract and schema field names in code, tests, and docs.
- **Scratch artifacts:** Before deleting generated files or fixtures, grep the repo for paths; run tests after cleanup.
- **Samples:** Contract examples should match what is shipped; future-only fields → `BACKLOG.md` or marked drafts.
- **CLI help vs README:** If you ship a CLI, keep `--help`, README, and tests aligned when help text is asserted.
- **JSON Schema:** Commit exported schema and test it against `model_json_schema()` (or your export script) so refactors cannot drift silently.
- **Integration tests:** Live tests **skipped by default** — [README](README.md) **Live API tests** (`API_SPEND_LIVE_TESTS=1`, keys, dump/raw paths). Full-stack: **`tests/test_api_spend_live.py`**. Mocked facade: **`tests/test_client.py`** — inject `SpendStore.open(":memory:")`, `ApiSpend(..., http_client=httpx.Client(MockTransport(...)))`, **close the HTTP client** after `ApiSpend.close()` (injected client not owned by facade). Keep default **`pytest`** fast.
- **PEP 668 / `venv`:** Many dev machines use a system Python that rejects `pip install` without a venv. Default to `python3 -m venv .venv`, `pip install -e ".[dev]"`, and `pytest` in docs and agent runs; add `.venv/` to `.gitignore`.
- **Small fixed string unions in contracts:** When the interface names a closed set of string values (e.g. `coverage`), `typing.Literal[...]` on Pydantic fields validates at parse time; serialized output remains plain strings for dashboards.
- **Public errors vs Pydantic:** Catch `pydantic.ValidationError` at the config boundary and re-raise as `ConfigError` with a short, joined message so callers only handle the documented exception types (`PLANNED_INTERFACE.md` §7).
- **Credential env names:** Use an explicit `provider → env var` map (§8); do not derive names from YAML `name` alone.
- **SQLite store path:** `SpendStore.open(file_path)` should `mkdir(parents=True)` for the DB’s parent directory. Use `PRAGMA page_count` × `PRAGMA page_size` for a portable **approximate** byte size (including `:memory:`). Persist datetimes as UTC ISO strings; normalize naive `datetime` to UTC when writing.
- **Pydantic v2 `BaseModel` constructors:** Prefer **keyword arguments** in tests and example code (`SpendRecord(provider=..., date=...)`). Positional args fail fast with an opaque `TypeError` (“takes 1 positional argument but N were given”), which is easy to misread as a pytest or import problem.
- **Mocking `httpx`:** Prefer **`httpx.MockTransport`** for adapter tests.
- **Billing adapters:** Document odd amount units or unlabeled time buckets in **`PLANNED_INTERFACE.md`** §3.1 so consumers do not infer behavior.
- **Library logging:** Use **`caplog.set_level(logging.INFO, logger="api_spend.client")`** (or the child logger under test) when asserting **`api_spend`** log lines; the root logger stays quiet by default. Keep **INFO** lines short; put long adapter errors on **DEBUG** per **`D-LOGGING-V1`**.

---

## 7. Maintaining this file

Update **section 6** when team practices evolve; keep **sections 1–5** aligned with the doc set you actually use.

**`BACKLOG.md` hygiene (scheduled):** At least **quarterly** (or each release), open **`BACKLOG.md`**: fold or delete items that have **shipped**; keep **`Vx-…`** rows short (locked future outcomes only, no v1 contract prose); trim **open backlog** bullets so they do **not** duplicate **`PLANNED_INTERFACE.md`**. Optional: add a recurring calendar reminder or release checklist line so this is not only ad hoc. **`TODO.md`** Phase 9 includes a checkbox that points here.

**`implementation-notes.md` hygiene:** Not on a fixed calendar — **on each release** or when editing code a phase retro touches, apply **Maintenance (pruning)** at the top of that file: drop obsolete bullets, compress stable sections, **promote** enduring lessons into **§6** here first, then shorten or remove duplicates. Keep **`### Phase N`** headings for archaeology.