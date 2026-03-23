# AI prompt snippets

**AI assistants and automated tooling:** Do **not** edit, reformat, append to, or rename this file. It is **human-maintained only**. Change it only when the user explicitly asks to modify **`ai-prompt-examples.md`** in that same message. This file has been added to `./.cursorignore`

## Decisions

```
Please give me more information about [DECISION].
```

```
Can we go through these one by one? You will provide your recommendation without taking any action. I will confirm or provide an alternative decision. You will update all documentation but not do any implementation. Once the decision is made and documentation updated, we will move on to the next decision.
```

## Interface planning

```
We’re building a python installable interface that will be used to fetch and provide data to a local browser dashboard. The purpose of this project is to provide information about how much money is being spent on various APIs.

I want the dashboard (which will be a separate project) to display the costs over time periods both in graphs and numbers.

Do you think that this project should keep track of the data or be a dumb fetcher who just provides the cost information? The cost information will come from a provided list of APIs. I am not sure if some, all, or none of the APIs allow cost information to be fetched over customized time intervals.

Think through step by step how to make this very easy to use for the dashboard UI developer. Focus only on the interface for now (don’t think about the implementation yet). Before you write your plan in PLANNED_INTERFACE.md, I would like your recommendation on my question above.
```

```
Do you agree with the framework selections? Any changes you’d recommend to increase simplicity, reliability, and extendability? Your recommendations do not need to be present in FRAMEWORKS.md. If a separate frameworks doc exists, trim or archive it so it does not contradict IMPLEMENTATION_PLAN.md.
```

## Implementation planning

```
Nice! Review `.cursor/rules/.cursorrules` and make a plan for implementing the planned interface. Think step by step and finally write it down in the IMPLEMENTATION_PLAN.md template. Speed is a very high priority for this project, are there things we can do about it or potential alternative solutions that we might be able to use?
```

## v1 todo planning

```
Please write a checklist in TODO.md of what to implement and how to test it (simply). Please iterate between implement, test, implement, test, etc. in the checkpoints. Base this checklist on the planned interface and IMPLEMENTATION_PLAN.md. Make sure to reference any required decisions that are required before implementing a todo.
```

```
Before we begin, can you take another pass through the documentation. Make sure everything is tight, clean, and concise. Make sure to identify any decisions that need to be made in DECISIONS as well as in the todo items that they are required for.
```

## Implementing todo items

```
Can you review with me how you plan to implement todo #<X> and #<Y>?
```

```
Can you split todo #<X> and #<Y> into more granular steps?
```

```
Is there anything that needs to be done before we implement #<X> and #<Y>? If there are any blocking decisions, provide your recommendations. If there are decisions or clarifications best done now (e.g. decisions needed during implementation), please describe and provide recommendations.
```

```
For your recommendations, my decisions are ... Do not implement. Update dall ocumentation needed for you to implement.
```

```
Please start implementing #<X> and #<Y>. Before you start, make sure there are no decisions that need to be made prior to implementation. If decisions need to be made, stop all implementation, review the decisions with me and what you recommend. Once all decisions are completed, begin implementing the requested todo items. Check off points on the checklist in the TODO.md template as you work. If all sub-checklist items are complete, place a check next to the checklist parent. Implement and run tests by yourself. Don’t stop to ask for confirmation. Make sure all documentation is up to date. Review and document any new decisions that emerged from the implementation. To keep an implement history, please review any issue, difficulty, or friction you encountered in implementing these checklist items and record them under the matching TODO checklist header in implementation-notes.md. Add any relevant lessons learned to COLLABORATION_AND_AI_RULES.md.
```

```
Please review any issue, difficulty, or friction you encountered in implementing these checklist items. Record this review under the matching TODO checklist header in implementation-notes.md.
```

```
Make a full pass through the docs for accuracy, clarity, and brevity. Prioritize useability for an AI agent like you over a human. In README.md, favor more thorough terminal command examples (e.g. include `cd /path/to/api-spend`).

Backlog hygiene: remove or fold shipped items; ensure Vx-… vs open ideas don’t duplicate contract text.
```

```
Based on how we have worked together so far, do you have any ideas for how the documentation could be improved to reduce documentation and implementation drift? Do not implement, recommend only.

Let's go back to review your remaining recommendations for how the documentation could be improved to reduce documentation and implementation drift. Do not implement, recommend only.
```