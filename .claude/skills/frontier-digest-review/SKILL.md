# /frontier-digest-review

**When to invoke:** After any change to the synthesis engine, prompt templates, or ranking logic. Also run after adding a new source for the first time.

---

## What This Skill Does

Audits the quality of a generated digest against Frontier Brief's quality standards. Catches issues before the user sees them.

---

## Quality Standards (from CLAUDE.md)

Every digest must meet all of these:
- Each item: 2–4 sentences, narrative style, no bullet points within the item
- Tone: like a knowledgeable colleague briefing you — not a press release, not academic, not robotic
- Every item has: `Source: [Publication Name](direct_url_to_original)` at the end
- Max 5–10 items per domain per digest cycle
- No duplicate topics across items in the same digest
- No items older than the 48-hour refresh window

---

## Steps

### 1. Generate a Test Digest
Trigger the synthesis pipeline in the development environment. If live sources are not yet available, use fixtures or a recorded fetch result.

### 2. Item Count Audit
For each domain in the digest:
- Count the number of items
- Flag any domain with more than 10 items — this must be cut
- Flag any domain with 0 items — is the source working?
- Report: `Domain: X items (PASS/FAIL — limit is 10)`

### 3. Citation Audit
For every item in the digest:
- Check: does it have `Source: [Name](url)` at the end?
- Check: is the URL a direct link to the specific item (tweet/paper/video/post) — not a homepage?
- Check: does the URL resolve to the correct content?
- Flag any item missing a citation as a **blocker** — it must not ship

### 4. Narrative Quality Audit
Review each item for:
- [ ] Is it 2–4 sentences? (flag if shorter than 1 sentence or longer than 6)
- [ ] Is it in narrative prose, not bullet points?
- [ ] Does it explain WHY the development matters — not just what happened?
- [ ] Is it written in a collegial, readable tone?
- [ ] Does it avoid press-release language ("groundbreaking", "revolutionary", "game-changing")?
- [ ] Is it specific enough that a reader knows what to click on?

### 5. Freshness Audit
- Check timestamps on all items
- Flag any item older than 48 hours from the current time
- Check if any items are exact duplicates of items from the previous digest cycle

### 6. Domain Tagging Audit
- Check that each item has at least one domain tag from the topics list in `ideas_v2.md`
- Check that tags are accurate — a paper about context windows should not be tagged "Product Launch"

### 7. Mobile Readability Check
Read the digest as if viewing it on a phone:
- Are item summaries short enough to read in 20–30 seconds each?
- Would the source link be easy to tap?
- Is the overall digest length reasonable for a mobile session?

### 8. Report
Produce a summary:
```
Digest Quality Report
=====================
Total items: X across Y domains

Volume: PASS/FAIL (domains over limit: ...)
Citations: PASS/FAIL (items missing citations: ...)
Narrative: PASS/FAIL (issues found: ...)
Freshness: PASS/FAIL (items out of window: ...)
Domain tags: PASS/FAIL

Issues requiring fix before shipping:
- [list any blockers]

Suggestions (non-blocking):
- [list any improvements]
```

Present the report to the user. Ask: "Any of these issues block you from using this digest?"

---

## Related ECC Skills
- `ecc:mle-reviewer` — Review the LLM pipeline producing the digest
- `ecc:rag-pipeline-reviewer` — Review retrieval and ranking feeding into synthesis
- `ecc:python-reviewer` — Review synthesis service code
- `/frontier-ui-check` — Run after digest review to confirm UI displays correctly
