# /frontier-plan

**When to invoke:** Before starting any sub-phase. This is the gate between "we agreed to do X" and "we are writing code for X." Never skip this.

---

## What This Skill Does

Produces a concrete, approved plan document for a single sub-phase before any implementation begins.

---

## Steps

### 1. Identify the Sub-phase
Read `CLAUDE.md` → Active Status table. Confirm with the user which sub-phase is being planned (e.g., "1a — Data pipeline for YouTube + arXiv").

### 2. Read the Context
- Read `ideas_v2.md` for product requirements and source list
- Read `CLAUDE.md` for tech stack, structure, and code standards
- Read any existing plan documents in `docs/plans/` for context on prior decisions

### 3. Run the Preference Gate
Check `CLAUDE.md` for the Preference Gate questions for the current phase. Ask the user all questions that have not already been answered. Use `AskUserQuestion` for choices where options are meaningful. Wait for answers before continuing.

### 4. Produce the Plan Document
Write the plan to `docs/plans/plan-<phase><sub>.md` (e.g., `docs/plans/plan-1a.md`).

The plan document must include:

```markdown
# Plan: Phase <N><sub> — <Name>

## Goal
One sentence: what does this sub-phase accomplish?

## Files to Create
- List every new file, with its path and a one-line description of its purpose

## Files to Modify
- List every existing file that will change, and what changes

## Dependencies
- External APIs, packages, or services needed (and whether they are already set up)

## Implementation Order
Numbered steps in the exact order to implement them.
Each step: action + file + what it produces.

## Risks & Open Questions
- Known unknowns that could block implementation
- Questions to resolve before or during implementation

## Acceptance Criteria
Checklist: how do we know this sub-phase is done?
- [ ] Criterion 1
- [ ] Criterion 2
...

## ECC Skills to Run
List which ECC skills run during and after this sub-phase.
```

### 5. Present and Wait for Approval
Show the plan to the user. Ask: "Does this plan look right, or would you like to change anything before I start?"

Do not write any implementation code until the user explicitly approves the plan.

### 6. Update CLAUDE.md Active Status
Once approved, update the Active Status table in `CLAUDE.md` to reflect the active sub-phase.

---

## Related ECC Skills
- `ecc:planner` — Sprint-level planning agent; run alongside this for complex sub-phases
- `ecc:architect` — For sub-phases with significant architecture decisions
- `/plan-prd` — If the sub-phase requires a new PRD section
