# /frontier-phase-gate

**When to invoke:** Before moving from one phase to the next. This is the end-of-phase quality gate. Nothing moves forward until this passes.

---

## What This Skill Does

Verifies that the current phase is truly complete — all sub-phases done, quality checks passed, and the user is satisfied — before the next phase begins.

---

## Steps

### 1. Identify the Current Phase
Read `CLAUDE.md` Active Status table. Confirm which phase is being closed.

### 2. Sub-phase Completion Check
For each sub-phase in the current phase (from `CLAUDE.md` Phase Guide):
- [ ] Is the sub-phase marked complete?
- [ ] Does a plan document exist in `docs/plans/` for it?
- [ ] Did `/code-review` run after it?

List any sub-phases that are incomplete. Do not proceed if any are unfinished.

### 3. Definition of Done Checklist
Pull the Definition of Done from `CLAUDE.md` for the current phase. Go through each item:
- Read the criterion
- Verify it is actually satisfied (check code, run a test, or ask the user to confirm)
- Mark PASS or FAIL

Present the full checklist to the user with status on each item.

### 4. Quality Checks
Run the following and confirm all pass:

**Code quality:**
- ECC `/code-review` on all files changed in this phase (if not already run)
- ECC `ecc:python-reviewer` on backend changes
- ECC `ecc:react-reviewer` on frontend changes (if applicable)

**Digest quality (if synthesis changed):**
- `/frontier-digest-review`

**UI quality (if frontend changed):**
- `/frontier-ui-check`

**Security (before any production-facing phase):**
- ECC `ecc:security-reviewer` or `/security-scan`

### 5. User Satisfaction Check
Ask the user:
```
Before we close Phase [N] and move to Phase [N+1]:

1. Have you used the Phase [N] build in a real session?
   (i.e., not just "it works" but "I actually used it for its intended purpose")

2. Is there anything about the current build that is not working
   the way you expected or hoped?

3. Any UI, digest quality, or source issues you noticed?

4. Are you satisfied enough to move to the next phase,
   or do you want to address something first?
```

Do not move to the next phase unless the user explicitly says they are ready.

### 6. Update CLAUDE.md
Once the gate is passed:
- Update the Active Status table: current phase → next phase, sub-phase → first sub-phase of next phase
- Mark completed sub-phases in the Phase Guide with ✅

### 7. Pre-gate for Next Phase
Read the Preference Gate questions for the next phase from `CLAUDE.md`. Ask them now, so the user can think about them before the next session begins. Record answers in `docs/plans/preference-gate-phase-<N+1>.md`.

---

## Related ECC Skills
- `/code-review` — Full code review before phase closes
- `ecc:python-reviewer` — Python-specific review
- `ecc:react-reviewer` — Frontend review
- `ecc:security-reviewer` — Security review
- `/frontier-digest-review` — Digest quality gate
- `/frontier-ui-check` — UI quality gate
- `/frontier-plan` — First thing to run in the next phase
