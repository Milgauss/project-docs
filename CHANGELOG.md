# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Contract “v1”** (see [`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md), [`DECISIONS.md`](DECISIONS.md)) aligns with this **1.0.0** package release: stable public surface for integrators; later work is semver-minor/major or backlog unless the contract is revised.

## [1.0.0] — 2026-03-23

### Added

- **`ApiSpend`** facade: config-driven `sync`, time-bucketed USD **`query`**, context manager lifecycle ([`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §4.3).
- **Providers** (billing APIs and snapshot-style estimates) with **`SpendRecord`** as the common row shape; registry in `api_spend.providers`.
- **SQLite store** (`SpendStore`) and query aggregation; env-based config paths and credentials ([`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §8).
- **stdlib logging** on `api_spend.*` loggers ([`PLANNED_INTERFACE.md`](PLANNED_INTERFACE.md) §4.4).
- **Packaging:** `pyproject.toml` (`api-spend`), **`py.typed`** for type checkers, **`LICENSE`** (MIT), this changelog.
- **CI:** pytest on Python 3.11 and 3.12; doc drift and public JSON Schema snapshot tests.

### Notes for integrators

- Install from a **private git URL** or **vendored clone** (see [`README.md`](README.md)); PyPI is optional.
- **Node-only** dashboards need a **Python boundary** (service, job, or subprocess): this repo is a **Python** library, not an npm package.

After you publish the tag, you can add a release link at the bottom of this file, for example: `[1.0.0]: https://github.com/<org>/<repo>/releases/tag/v1.0.0`.
