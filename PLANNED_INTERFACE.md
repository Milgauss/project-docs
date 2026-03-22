# Planned interface (design contract)

This document is the **normative contract** for how **API Spend** behaves from an **end user** and **integrator** perspective (CLI, HTTP API, file formats, etc.—adapt sections to your surface). It specifies **behavior and structured output**, not internal module layout—that lives in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

**Related:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`DECISIONS.md`](DECISIONS.md) (**`D-…`**, v1) · [`TODO.md`](TODO.md) · [`BACKLOG.md`](BACKLOG.md) (**`Vx-…`** pre-contract + open backlog for **v2+**).

---

## 1. Who uses this interface?

| Actor | Goal |
|--------|------|
| **Primary integrator** | (e.g. automation, agent, another service) — stable fields, explicit errors, predictable exit codes. |
| **Human operator** | Configure inputs, run jobs, debug failures, skim output without reading raw payloads. |

---

## 2. Design principles

1. **Explicit over magic:** Identifiers, paths, and failure modes are documented and stable where they are part of the contract.
2. **Fail soft when multiple units of work run together:** If one unit fails, others may still succeed; represent failures in structured output, not only process exit codes.
3. **Secrets:** Never require secrets on the command line in documentation; use environment variables and optional config files; document names once.
4. **Stable machine-readable output** where integrators depend on it; human-friendly views are optional.
5. **Human-maintained inputs:** Long-lived lists (URLs, accounts, feature flags) live in files or systems **humans** edit; the primary command **reads** them and does not silently mutate them unless that is an explicit, documented feature.

Adapt, add, or remove principles to match your product.

---

## 3. Invocation

### 3.1 Entrypoint

**v1 command name (`D-RELEASE-NAME` in [`DECISIONS.md`](DECISIONS.md)):** **`api-spend`** — document the same string in packaging config (e.g. `pyproject.toml` **`[project.scripts]`**, `package.json` **`bin`**, etc.).

### 3.2 Subcommands / operations

List subcommands or modes (e.g. **`process`**, **`validate-config`**, **`version`**). State which are **v1** and which are **draft** for a future major (see [`BACKLOG.md`](BACKLOG.md)).

### 3.3 Global flags / options

| Flag / env | Purpose |
|------------|---------|
| *(add rows)* | |

**Environment variables:** document each name, when it is required, and validation rules (e.g. a **`validate-config`** command fails fast when required vars are missing).

### 3.4 Path resolution (if applicable)

State how **relative** paths in config files vs on the command line resolve (config file directory vs current working directory is a common split).

---

## 4. Main operation (v1)

Describe the default “happy path”:

- **Inputs:** files, flags, stdin, etc.
- **Precedence:** if multiple sources apply, define merge order and collision rules.
- **Output:** stdout vs files; JSON vs other formats.
- **Side effects:** state files, databases, network calls—when they happen and when they are skipped (e.g. **dry-run**).

---

## 5. Output shape

Define the stable schema (field names, null vs omitted keys, per-item error fields). If you publish **JSON Schema**, point to [`schemas/`](schemas/) and state that schema and this section must stay aligned.

---

## 6. Errors and exit codes

| Code | Meaning |
|------|---------|
| **0** | Success as defined for this command (may still include partial failures inside structured output if that is your contract). |
| **1** | *(define)* |
| **2** | *(define — e.g. usage / validation)* |

List stable **`code`** strings or error enums for machine parsing.

---

## 7. Future versions (non-normative here)

Draft behavior for **v2+** lives in [`BACKLOG.md`](BACKLOG.md) as **`Vx-…`** rows and open sections until you **promote** the text into this file.

---

## 8. Changelog pointer

Track interface-breaking changes in release notes or a dedicated section when you ship.
