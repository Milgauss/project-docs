# Initial Product Requirements

> **⚠️ NOT A SOURCE OF TRUTH — HISTORICAL CONTEXT ONLY**
> This document contains the original requirements used to bootstrap `PLANNED_INTERFACE.md`. 
> It is intentionally NOT updated as development progresses. 
> **Agents:** Do NOT read this file to make implementation decisions (unless the human explicitly asks you to read it during initial Bootstrap via Prompt 2). If you need the current contract, read `PLANNED_INTERFACE.md`.

---

### 💡 For the Human: How to use this file in a new project
When starting a new project with this template, paste your product requirements below, and then use these prompts in your Cursor chat to kick off the project safely.

**Before starting, ensure Taskmaster MCP is configured:**
Taskmaster allows Cursor to track micro-steps without polluting our high-level markdown files. It stores its state locally in your project.
1. **Initialize Taskmaster in your project:** Run `npx task-master-ai init` in your terminal to initialize the local `.taskmaster` folders and config files for this specific project.
2. In Cursor Settings > Features > MCP, add a new server:
   - **Name:** `task-master`
   - **Type:** `command`
   - **Command:** `npx -y task-master-ai`
3. (Optional) If you are modifying the `.cursor/mcp.json` file directly, ensure you add your LLM API keys to the `env` object for the server if required by your specific provider.
4. Restart Cursor completely to ensure the MCP server is loaded.
5. In the Cursor chat, click the "Tools" or "MCP" icon to verify that the tools are available.

**Prompt 1: Start the Bootstrap Process**
> *"Hello! I have just copied a new project documentation template into this folder. This project will be a [briefly describe app, e.g., Next.js SaaS app]. Please familiarize yourself with `README.md` and then initiate the `BOOTSTRAP.md` process with me so we can set up the basic project configuration."*

**Prompt 2: Transition from Bootstrap to Interface Planning**
*(Use this only after BOOTSTRAP.md is complete and renamed to INIT_LOG.md)*
> *"Now that bootstrap is done, let's move to Interface Planning. Please read `_human-docs/INITIAL_REQUIREMENTS.md` and follow its references to understand the product requirements. Use that knowledge to flesh out `PLANNED_INTERFACE.md` starting at Section 1. Once you have written `PLANNED_INTERFACE.md`, treat it as the absolute Source of Truth going forward and do not rely on the initial requirements document anymore."*

**Prompt 3: Transition from Interface Planning to Implementation Planning**
*(Use this after you are satisfied with PLANNED_INTERFACE.md)*
> *"PLANNED_INTERFACE.md looks great. Let's move on to the implementation plan. Please flesh out `PLAN.md` (Sections 1-3 only), `DECISIONS.md`, and any v2+ ideas into `BACKLOG.md` based strictly on what we just agreed upon in `PLANNED_INTERFACE.md`. Do not start generating phase checklists in PLAN.md yet until I approve the architecture."*

**Prompt 4: Generating the Phase Checklists**
*(Use this after you have approved the architecture and stack in PLAN.md)*
> *"The architecture and stack in `PLAN.md` Sections 1-3 are approved. Please change the Design Status checkbox to `[x]` and generate the feature-level Phase Checklists in Section 4. Base this strictly on `PLANNED_INTERFACE.md` and our agreed architecture. Break the work down into feature-level Epics (e.g., 'Implement JWT Middleware' or 'Build Checkout UI') and group them using an 'Implement -> Test -> Implement -> Test' pattern for each feature. Do not make them too broad ('Build Backend'), but do NOT break them down into file-level micro-steps either—we will use Taskmaster for that later. For any step that depends on an unresolved product or technical choice, reference a `Refs: D-...` tracker from `DECISIONS.md`."*

**Prompt 5: Document Polish Before Implementation**
*(Use this after the Phase Checklists are generated but before you start coding)*
> *"Before we begin implementing the checklists, please do a final pass over `PLANNED_INTERFACE.md`, `PLAN.md`, and `DECISIONS.md`. Make sure the language is tight, clean, and concise. Ensure that all cross-references (like `Refs: D-...`) map correctly between files. **CRITICAL:** Do NOT alter the structural headers, agent instructions, `[ ]` checklist formatting, or any of the existing agent control mechanisms in these templates. Only polish the project-specific content we just wrote for clarity and brevity."*

**Prompt 6: Pre-Flight Check & Taskmaster Setup**
*(Use this before asking the agent to implement specific Phase Checklist items)*
> *"I'd like to implement items [X] and [Y] from `PLAN.md`. 
> 1. Review these items against `PLANNED_INTERFACE.md` and `DECISIONS.md`. 
> 2. Are there any pending `D-...` decisions, missing technical details, or required clarifications that block this work? If so, stop and provide your recommendations for resolving them. 
> 3. If there are no blockers, use the Taskmaster MCP to create a structured task graph for this work. Create a parent Epic for the `PLAN.md` items, and break it down into granular micro-steps. Wait for my approval of the Taskmaster graph before writing any code."*

**Prompt 7: Execute Implementation via Taskmaster**
*(Use this to kick off autonomous coding after Prompt 6 is approved)*
> *"The Taskmaster graph is approved. Please begin execution.
> 1. Query Taskmaster for the first pending sub-task.
> 2. Implement the item autonomously. Run tests yourself and fix any errors.
> 3. Once successful, mark that node complete in Taskmaster.
> 4. Automatically proceed to the next pending sub-task in Taskmaster until the parent Epic is complete.
> 5. **Sync to PLAN:** Only when the entire Taskmaster Epic is complete, check off `[x]` the corresponding high-level items in `PLAN.md`.
> 6. **Doc Updates:** Review and record any new technical decisions that emerged in `DECISIONS.md`. 
> 7. **Retrospective:** Log any friction, bugs, or architectural difficulties in `implementation-notes.md`. Add any systemic lessons learned to `COLLABORATION_AND_AI_RULES.md`."*

**Prompt 8: Post-Implementation Retrospective**
*(Use this immediately after the agent finishes a complex implementation step, to ensure hard-learned lessons are saved for future chat sessions)*
> *"Implementation looks good. Now, please review any issues, difficulties, or friction you encountered in implementing these checklist items. Record this review under the matching Phase/Checklist header in `implementation-notes.md`. If you learned anything about how to interact with this specific codebase or framework that future agents should know, add a brief rule to `COLLABORATION_AND_AI_RULES.md`."*

**Prompt 9: Post-Implementation Document Polish**
*(Use this after coding is complete and you have updated the checklists and notes, to ensure all core contract documents accurately reflect any shifts that occurred during implementation)*
> *"Now that we have finished the implementation and recorded our retrospectives, please do a final polish pass over `PLANNED_INTERFACE.md`, `PLAN.md`, and `DECISIONS.md`. Check that the technical realities of what we just built match the architectural promises in the contract. Clean up any stale context, ensure cross-references are accurate, and make the language tight and concise. **CRITICAL:** Do NOT alter the structural headers, agent instructions, `[ ]` checklist formatting, or any of the existing agent control mechanisms."*

**Prompt 10: Deep Debugging / Stuck State**
*(Use this when tests are failing or the agent is stuck in a loop of broken code)*
> *"We are stuck on an error: [paste error/describe bug]. Stop all feature implementation. Shift to debugging mode. 
> 1. Do not guess or write speculative fixes. 
> 2. Read the relevant code and cross-reference it with `PLANNED_INTERFACE.md` to verify the expected behavior. 
> 3. Add console logs or use debug tools to gather concrete evidence of the state. 
> 4. Present your findings on the root cause and propose a targeted fix. Wait for my approval before modifying the code."*

**Prompt 11: Kicking off a Complex Sub-Task (DEPRECATED)**
*(This prompt is no longer needed. Taskmaster MCP handles complex sub-tasks dynamically during Prompt 6. Do not use `active-task.md`.)*

**Prompt 12: Promoting a Backlog Item to Active Contract**
*(Use this weeks/months later when adding a single isolated feature to an established project)*
> *"I would like to start building [Feature Name] / [Vx-...] from the `BACKLOG.md`. Please review the current `PLANNED_INTERFACE.md` and `PLAN.md`. Propose the necessary updates to the Interface contract to support this new feature. Do not write any application code yet. Let's agree on the interface additions first, then we will generate the implementation checklist."*

**Prompt 13: Wrapping up V1 (The Freeze)**
*(Use this when all current checklists are complete, tests are passing, and you are ready to conclude the current phase)*
> *"All V1 implementations are complete and working. Please perform a major version wrap-up.
> 1. Do a final review of `PLAN.md` to ensure all checklists are fully marked `[x]`. 
> 2. Move all completed `D-...` items in `DECISIONS.md` from Section 3 (Pending) to Section 2 (Shipped).
> 3. Update `PLANNED_INTERFACE.md` to reflect that V1 is finalized.
> 4. Review `BACKLOG.md` and prepare the workspace to begin migrating `Vx-...` items into the active contract. Do not start implementing V2 yet; just finalize the current documentation state."*

**Prompt 14: Kicking off the Next Major Version (V2+)**
*(Use this to restart the planning loop for a new major phase. **Note:** Paste any new product requirements into `_human-docs/V2_PRD.md` before running this.)*
> *"We are kicking off V2. Please read `_human-docs/INITIAL_REQUIREMENTS.md` and follow its references to understand the V2 requirements. Review any existing `Vx-...` ideas in `BACKLOG.md`. Just like we did in Phase 1, use that knowledge to update `PLANNED_INTERFACE.md` with the new V2 architecture and scope. Do not update `PLAN.md` or write code yet. Treat this as a clean reset to the Interface Planning phase. Once we agree on the V2 Interface, we will move to Prompt 3."*

---

### 🔄 The Development Loop
For large projects, **do not execute all checklist items at once.** Instead, cycle through Prompts 6, 7, 8, and 9 for just 1-3 related checklist items at a time. This keeps the agent's context window fresh, ensures tests pass incrementally, and prevents cascading architectural errors. 

Once Prompts 6-9 are complete for the current chunk, start the loop over at Prompt 6 for the next batch of items.

When an entire major version is complete, use Prompts 13 and 14 to freeze the current state and restart the loop for the next major version.

---

## Product Requirements

Instead of pasting massive requirements here, it is recommended to keep them in dedicated files within the `_human-docs/` folder and reference them below.

### V1 Requirements
* **Reference:** `_human-docs/V1_PRD.md` (Create this file and paste your initial requirements there).

### V2+ Requirements
* **Reference:** `_human-docs/V2_PRD.md` (Create this file when ready to use Prompt 14).
