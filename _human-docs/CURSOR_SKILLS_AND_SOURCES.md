# Cursor skills and AI setup (inventory)

Human-first inventory of **template-shipped skills**, **upstream sources** (for updates), **Cursor rules** that pair with them, and **optional** third-party skills to mirror into `.cursor/skills/`. Keep this under `_human-docs/` (or equivalent) so it stays outside default agent indexing (see `.cursorignore`).

## Skills

| Skill | Role | Installed path (this template) | Source and updates |
|--------|------|----------------------------------|---------------------|
| **code-reviewer** | Code review posture, optional scripts, reference scaffolds | `.cursor/skills/code-reviewer/` | **Package:** [`claude-code-templates`](https://www.npmjs.com/package/claude-code-templates) (see [Claude Code Templates](https://aitmpl.com), [docs](https://docs.aitmpl.com)). **Template id:** `development/code-reviewer`. **Refresh:** `npx claude-code-templates@latest --skill development/code-reviewer` (defaults to `.claude/skills/code-reviewer/`; merge into `.cursor/skills/code-reviewer/` for Cursor). |
| **docs-cleaner** | Consolidate redundant docs without losing value | `.cursor/skills/docs-cleaner/` | **Repo:** [`daymade/claude-code-skills`](https://github.com/daymade/claude-code-skills) (`docs-cleaner`). **Install / refresh:** `npx skills add https://github.com/daymade/claude-code-skills --skill docs-cleaner -y` ([`skills` CLI](https://www.npmjs.com/package/skills)). Output under `.agents/skills/docs-cleaner`; this template also mirrors `.cursor/skills/docs-cleaner/` for Cursor—re-sync after upgrades. |

### Operating notes

- **code-reviewer:** `SKILL.md` is the entry point. `references/` are upstream starters—replace with team standards. `scripts/` are optional Python scaffolds. Version-control `.cursor/skills/<name>/` so the team shares skills.
- **docs-cleaner:** Workflow: discovery → value analysis (keep / condense / delete) → consolidation plan (metrics) → single source of truth + link fixes. Detail: `references/value_analysis_template.md` in the skill folder. Triggers: “clean up docs”, “merge these docs”, overlapping markdown guides. **Contract-first repos:** safe for guides and README sprawl; do **not** merge or delete normative contracts (`PLANNED_INTERFACE.md`, locked `DECISIONS.md` rows) unless the human is driving a contract change.

**Example agent prompts (docs-cleaner):**

```text
Use docs-cleaner on docs/onboarding/ + README.md: map overlap, propose one doc (keep/condense/delete),
before/after line counts, apply edits, fix links. Do not change PLANNED_INTERFACE.md or DECISIONS.md.

# shorter
Clean up redundant markdown in docs/api/: one source of truth; list kept vs condensed; no contract files.
```

Agents should follow `.cursor/skills/docs-cleaner/SKILL.md`. If you asked plan-first, confirm before deleting files.

## Related Cursor rules (not skills)

| Rule | Path | Role |
|------|------|------|
| Code review standards | `.cursor/rules/code-review-standards.mdc` | SRP, DRY, typing, React, async, simplify—scoped by **globs** (tighten per repo layout below). |

## Other template rules (reference)

| File | Role |
|------|------|
| `.cursor/rules/implementation-decisions.mdc` | Contract-first workflow (`PLANNED_INTERFACE.md`, `PLAN.md`, `DECISIONS.md`, …). |
| `.cursor/rules/agent-workflow.mdc` | Agent read order, Taskmaster notes. |
| `.cursor/rules/markdown-agent-priority.mdc` | Markdown / SoT authoring priorities. |

Check each file’s frontmatter for `alwaysApply` and `globs`.

## Tightening review-rule globs

`code-review-standards.mdc` ships with **broad** globs (common extensions plus `scripts/`, `test/`, `tests/`, `__tests__/`). Narrow them to product code only: open the file, keep `alwaysApply: false` when using globs, replace `globs:` with paths that match **only** your app and packages.

**Example (single frontend app—copy and adapt; not universal):**

```yaml
globs:
  - "apps/web/**/*.{ts,tsx}"
  - "apps/web/scripts/**/*"
  - "apps/web/**/*.test.{ts,tsx}"
  - "apps/web/**/__tests__/**/*"
```

**Same idea elsewhere:** monorepo → `packages/*/src/**/*.{ts,tsx}` (plus `scripts`, tests); split stacks → `backend/**/*.py` vs `frontend/**/*.{ts,tsx}`; Python service → `src/**/*.py` and `tests/**/*.py`. After editing, open one file that should match and one that should not; confirm Cursor attaches the rule only where intended.

## Optional skills (Claude-oriented; mirror into Cursor)

Use `npx skills add …` (or the noted CLI), then copy or sync to `.cursor/skills/<name>/SKILL.md`. Re-run installers to upgrade. Some entries need MCP config, CLIs, or cloud credentials—follow upstream docs.

| Area | Install / entry | Notes |
|------|-----------------|-------|
| Remotion | `npx skills add remotion/agent-skills` | e.g. `/remotion` — short product demo with charts/transitions |
| Google Workspace | `npm install -g @googleworkspace/cli`; MCP: `gws mcp -s drive,gmail,calendar,sheets`; skill: `npx skills add https://github.com/googleworkspace/cli` | Often need both Cursor MCP and the skill |
| Antigravity | `npx antigravity-awesome-skills - claude` | Starter `@` skills and bundles below |
| PlanetScale | `brew install planetscale/tap/pscale`; `pscale auth login`; `npx skills add planetscale/agent-skill` | Branches, connection, DDL, deploy requests (`pscale branch create`, `pscale deploy-request create`, …) |
| Shannon (pentest) | `npx skills add unicodeveloper/shannon` | Docker; Anthropic API key per upstream |
| Excalidraw | `npx skills add https://github.com/coleam00/excalidraw-diagram-skill --skill excalidraw-diagram` | Architecture, sequence, and flow diagrams |

### Antigravity: starter skills and bundles

| Skill | Focus |
|-------|--------|
| `@brainstorming` | Structured planning before coding |
| `@architecture` | System design and component structure |
| `@debugging-strategies` | Troubleshooting playbooks |
| `@api-design-principles` | API shape, consistency, versioning |
| `@security-auditor` | Security-focused review |
| `@lint-and-validate` | Lightweight quality checks |
| `@create-pr` | Clean pull requests |
| `@doc-coauthoring` | Technical documentation |

```text
/brainstorming help me plan the data model for a multi-tenant SaaS
/security-auditor review the authentication flow in src/auth/
/api-design-principles review the REST endpoints in routes/
```

| Bundle | Includes |
|--------|----------|
| **Web Wizard** | frontend-design, api-design-principles, lint-and-validate, create-pr |
| **Security Engineer** | security-auditor, lint-and-validate, debugging-strategies |
| **Essentials** | brainstorming, architecture, debugging-strategies, doc-coauthoring, create-pr |

### Shannon: CLI examples

```bash
/shannon http://localhost:3000 myapp
/shannon - scope=xss,injection http://localhost:8080 frontend
/shannon - workspace=audit-q1 http://staging.example.com backend-api
/shannon status
/shannon results
```

Pipeline (summary): pre-recon → recon → parallel analysis (injection, XSS, SSRF, auth, authz) → exploitation → reporting (executive summary + PoCs). Example coverage: SQL/command/SSTI/NoSQL injection; XSS (reflected, stored, DOM, uploads, mutation XSS); SSRF; broken auth (JWT, session, CSRF, MFA); broken authz (IDOR, privilege escalation, path traversal, mass assignment); and related classes per upstream.

### Excalidraw: example prompts

- Request path through API gateway, auth middleware, and downstream services
- Multi-tenant SaaS with per-tenant schemas and a shared analytics layer
- OAuth2 PKCE sequence: browser, authorization server, resource server
