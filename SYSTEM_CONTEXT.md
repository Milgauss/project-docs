# System context (broader project)

**Status:** Template — replace comments and tables when this repo has a defined place in a parent system.

**Normative behavior** stays in [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) and related contract docs. This file is **context only** for humans and AI agents: how *this* repository is expected to be used inside a larger product, monorepo, or deployment. If anything here conflicts with the contract, **the contract wins** (then update this file).

---

## 1. Role in the larger system

<!-- One short paragraph: what job api-spend performs for the parent (e.g. local spend sync + query for dashboards). -->

## 2. Parent project

<!-- Working name, repo or workspace location, primary stack (languages, orchestration). -->

## 3. Boundary: this repo vs parent / siblings

| In **this** repo (`api-spend`) | In the **parent** or **sibling** packages |
|-------------------------------|-------------------------------------------|
| <!-- e.g. sync, store, query, adapters --> | <!-- e.g. UI, auth, billing UI, orchestration --> |

## 4. Integration pattern

<!-- How the parent invokes this library: import path, submodule, path dependency, scheduled job, sidecar, subprocess, etc. Link to README “For dashboard integrators” if that already matches. -->

## 5. Runtime and data flow

<!-- Who runs `sync` and how often; where `config.yaml` / env live; store path or exported artifacts; who calls `query` and how results reach the UI. -->

## 6. Assumptions and constraints

<!-- e.g. single-writer SQLite, secrets only via env, Node never imports this package — only what helps future edits, not a copy of §8. -->

## 7. Related repos or packages

| Name | Relationship |
|------|--------------|
| <!-- e.g. dashboard --> | <!-- consumer / dependency --> |

## 8. Open questions

<!-- Undecided integration details. Do not treat answers here as contract until promoted into PLANNED_INTERFACE / DECISIONS / BACKLOG as appropriate. -->
