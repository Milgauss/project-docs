---
name: code-reviewer
description: >-
  Reviews code and docs for quality, security, and consistency. Use when
  reviewing pull requests, diffs, or when the user asks for a code review.
  In this repo, cross-check contract docs (PLANNED_INTERFACE, PLAN, DECISIONS)
  and public-surface rules before approving changes.
---

# Code reviewer

Toolkit aligned with [claude-code-templates](https://github.com/aitmpl/claude-code-templates) skill `development/code-reviewer` (installed under `.claude/skills/` if you ran `npx`). This copy lives at `.cursor/skills/code-reviewer/` for Cursor agents.

## Project integration (this repository)

This workspace is **contract-first** (`PLANNED_INTERFACE.md` > `PLAN.md` > code). When reviewing work here:

1. **Read order** — Follow [`README.md`](../../README.md) ([For coding agents](../../README.md#for-coding-agents), [Cold start](../../README.md#cold-start)): `PLANNED_INTERFACE.md` (SoT) → `PLAN.md` → `DECISIONS.md` when `PLAN.md` references `D-…` → optional `BACKLOG.md`.
2. **Behavior changes** — No new normative behavior without updating the contract and decision refs; see [`AGENTS.md`](../../AGENTS.md) and [`COLLABORATION_AND_AI_RULES.md`](../../COLLABORATION_AND_AI_RULES.md) for public API / ritual.
3. **Docs-only tasks** — If the human scoped docs-only, narrow reads per [`README.md` human scope](../../README.md#human-scope); still update SoT when behavior documented there changes.

Flag **contract drift** (code or docs contradicting `PLANNED_INTERFACE.md` / locked `DECISIONS.md` entries) as blocking.

## Review checklist (agent)

- Correctness and edge cases; tests or doc evidence where applicable.
- Security (inputs, secrets, authz) for any executable or API surface.
- Consistency with repo naming, structure, and existing patterns.
- **SoT:** Changes that affect the public or documented contract match `PLANNED_INTERFACE.md` and any `Refs: D-…` in `PLAN.md` / `DECISIONS.md`.
- **Noise:** Prefer focused diffs; avoid drive-by refactors unless requested.

Optional feedback labels: **Must fix** · **Should fix** · **Suggestion** · **Nit**.

## Reference files (template scaffolds)

The files under `references/` are **starter outlines** from the upstream template. Replace them with your team’s real standards over time. They are still useful as section prompts:

| File | Intent |
|------|--------|
| [references/code_review_checklist.md](references/code_review_checklist.md) | Review dimensions and patterns |
| [references/coding_standards.md](references/coding_standards.md) | Style and structure expectations |
| [references/common_antipatterns.md](references/common_antipatterns.md) | Things to call out |

Read them when a deeper pass is needed; keep `SKILL.md` as the entry point.

## Scripts (optional)

Lightweight Python scaffolds for wiring your own checks. Run from this skill directory so `scripts/` resolves:

```bash
cd .cursor/skills/code-reviewer

python scripts/pr_analyzer.py /path/to/repo-or-subdir
python scripts/code_quality_checker.py /path/to/target [--verbose]
python scripts/review_report_generator.py /path/to/target
```

They currently validate paths and emit a minimal report; extend the classes if you want real analysis.

## Tech stack (upstream blurb)

The template mentions TypeScript, JavaScript, Python, Go, Swift, Kotlin, and common web/cloud stacks. Adapt to whatever this repo actually uses.

## Resources

- Pattern prompts: `references/code_review_checklist.md`
- Standards outline: `references/coding_standards.md`
- Antipattern prompts: `references/common_antipatterns.md`
- Scripts: `scripts/`
