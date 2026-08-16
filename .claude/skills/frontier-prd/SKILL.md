# /frontier-prd

**When to invoke:** Phase 0b (initial PRD), and before each new major phase begins.

---

## What This Skill Does

Writes a formal Product Requirements Document for the current or upcoming phase. The PRD is the contract between product vision and implementation. No phase starts without one.

---

## Steps

### 1. Read the Sources
- Read `ideas_v2.md` in full — this is the product vision
- Read `CLAUDE.md` — tech stack, phase guide, and non-negotiables
- Read any existing PRDs in `docs/prd/` to maintain continuity

### 2. Identify the Scope
Confirm with the user which phase the PRD covers. Ask:
- "Is this PRD for Phase 1 specifically, or should it cover the full roadmap?"
- "Are there any requirements from ideas_v2.md that you want to adjust before I write the PRD?"

### 3. Write the PRD

Save to `docs/prd/prd-phase-<N>.md`. Structure:

```markdown
# Frontier Brief — PRD Phase <N>: <Phase Name>

## Overview
What this phase delivers, in 2–3 sentences.

## Goals
- Goal 1
- Goal 2

## Out of Scope
What is explicitly NOT being built in this phase (to avoid scope creep).

## User Stories
For each feature:
**As a user, I want to [action] so that [benefit].**
Acceptance criteria:
- [ ] ...

## Functional Requirements

### Feature Name
- Requirement 1
- Requirement 2
- Edge case handling

(repeat for each feature)

## Non-Functional Requirements
- Performance: page load < X seconds on mobile
- Reliability: fetcher failures must not crash the pipeline
- Citation: every digest item must link to the original source

## Data Models
Define new or modified database tables and fields.

## API Contracts
For each new endpoint:
- Method + path
- Request schema
- Response schema
- Error responses

## UI Requirements
- Mobile behavior at 375px
- Desktop behavior at 1280px
- Specific component behavior (filter chips, cards, etc.)

## Source Requirements (if applicable)
Which sources are in scope for this phase, and what fields each must provide.

## Digest Quality Requirements
Volume cap, citation format, narrative style — confirm from CLAUDE.md.

## Dependencies
External APIs, services, or prior phases that must be complete first.

## Open Questions
Things not yet decided that must be resolved before implementation.

## Definition of Done
- [ ] All user stories implemented
- [ ] /code-review passed
- [ ] /frontier-ui-check passed (if frontend changes)
- [ ] /frontier-digest-review passed (if synthesis changes)
- [ ] /security-scan passed
```

### 4. Review with User
Present the PRD. Ask: "Does this capture what you want to build in this phase? Anything missing or wrong?"

Do not proceed to planning or implementation until the PRD is approved.

### 5. Run ECC /plan-prd
After writing the initial draft, also invoke ECC `ecc:planner` or `/plan-prd` for an additional structured planning pass.

---

## Related ECC Skills
- `/plan-prd` — ECC's PRD planning skill; run after this for a second pass
- `ecc:planner` — Sprint-level decomposition after PRD is approved
- `/frontier-plan` — Sub-phase planning (runs after PRD approval)
