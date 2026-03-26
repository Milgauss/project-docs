# Agents

Thin entry point for tools that look for **`AGENTS.md`**. **Normative detail lives elsewhere** — do not duplicate contract text here.

**Precedence:** `PLANNED_INTERFACE.md` > `PLAN.md` > code.

**SoT table:** [`PLANNED_INTERFACE.md` §0](PLANNED_INTERFACE.md#sources-of-truth)

**Full agent workflow + task routing + doc index:** [`README.md` — For coding agents](README.md#for-coding-agents) (includes [Task → open first](README.md#task-first-open), [Cold start](README.md#cold-start), [Human: scope hint](README.md#human-scope), [`rg` registers](README.md#rg-registers)).

**Complex tasks (state tracked on disk):** Use **Taskmaster MCP** for tracking execution micro-steps.

**Taskmaster MCP Setup:** If not initialized, human runs `npx task-master-ai init` in the terminal and adds `npx -y task-master-ai` as a Cursor command MCP.
