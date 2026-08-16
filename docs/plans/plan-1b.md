# Plan: Phase 1b — Synthesis Engine

## Goal
Take ranked `FetchedItem` objects from the Phase 1a pipeline and use the Claude API to produce narrative `DigestItem` summaries — 2–4 sentences each, with a citation — ready to be persisted in Phase 1d.

---

## Files to Create

| File | Purpose |
|------|---------|
| `backend/app/services/synthesis/prompts.py` | System prompt and per-domain user prompt template; all prompt strings live here, never inline in callers |
| `backend/app/services/synthesis/claude_client.py` | Async Anthropic SDK wrapper; single public function `complete(messages)` that returns the response text |
| `backend/app/services/synthesis/synthesizer.py` | Orchestration: groups items by domain → calls Claude → parses JSON response → returns `list[DigestItem]` |
| `backend/tests/synthesis/__init__.py` | Package marker |
| `backend/tests/synthesis/test_synthesizer.py` | Tests: correct output shape, citation present, ≤5 items/domain, malformed JSON handled, API error handled |

---

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/services/synthesis/__init__.py` | No change — already exists as package marker |
| `backend/tests/conftest.py` | Confirm `ANTHROPIC_API_KEY` env var is present (it already is — no change needed) |

---

## Dependencies

| Dependency | Status |
|-----------|--------|
| `anthropic` Python SDK | Already in `requirements.txt` (v0.34.2) |
| `ANTHROPIC_API_KEY` | Set in Railway Variables — available at runtime |
| `FetchedItem` dataclass | Defined in `base.py` — Phase 1a complete |
| `DigestItem` SQLAlchemy model | Defined in `models.py` — Phase 1a complete |

---

## Design Decisions

### Input / Output contract
`synthesizer.synthesize(items: list[FetchedItem]) -> list[DigestItem]`

- Input: all ranked `FetchedItem`s for one refresh cycle (already capped at 10/domain by ranker)
- Output: `DigestItem` ORM objects (not yet persisted — Phase 1d writes them to DB)

### Batching strategy
One Claude API call per domain group (not one call per item). This is cheaper and produces more coherent domain summaries. Each call gets up to 5 items (ranker caps at 10; synthesizer further caps at 5 before sending to Claude, per CLAUDE.md volume discipline).

### Prompt design
Claude is asked to return a **JSON array**. Each element: `{narrative, source_name, source_url}`. Using structured JSON output avoids fragile text parsing. If JSON parsing fails, that domain's batch is skipped and the error is logged — the pipeline continues.

### Citation format
Each `narrative` field must end with: `Source: [Source Name](direct_url)`. This is enforced in the prompt and validated in the synthesizer before accepting Claude's output.

### Model
`claude-sonnet-5` per CLAUDE.md.

---

## Implementation Order

1. **`prompts.py`** — Write `SYSTEM_PROMPT` and `make_user_prompt(domain, items)` function. The user prompt serialises each item's title, summary, source_name, and source_url as a numbered list and instructs Claude to return JSON.

2. **`claude_client.py`** — Async wrapper: `async def complete(system: str, user: str) -> str`. Uses `anthropic.AsyncAnthropic`, model `claude-sonnet-5`, max_tokens=2048. Returns the text content of the first message block. Raises on API errors (caller handles).

3. **`synthesizer.py`** — Main logic:
   - `_group_by_domain(items)` → `dict[str, list[FetchedItem]]`
   - `_parse_response(raw_json, fetched_items)` → `list[DigestItem]` — validates citation present, maps back source metadata
   - `async def synthesize(items, cycle_id)` → `list[DigestItem]` — for each domain group: cap at 5, call Claude, parse, collect results with `asyncio.gather(..., return_exceptions=True)`

4. **`tests/synthesis/test_synthesizer.py`** — Tests with `AsyncMock` on `claude_client.complete`:
   - Returns correct number of DigestItems
   - Each narrative is non-empty
   - Each source_url is present and matches input
   - Malformed JSON from Claude → empty list for that domain, no crash
   - API error on one domain → other domains still return results

---

## Risks & Open Questions

| Risk | Mitigation |
|------|-----------|
| Claude returns malformed JSON | Catch `json.JSONDecodeError`, log, skip domain — tested explicitly |
| Narrative too short or too long | Validated in prompt ("2–4 sentences") — not enforced in code (impractical to count sentences reliably) |
| Anthropic API rate limit | `anthropic` SDK raises `RateLimitError` — propagate up to caller, let Phase 1d handle retry |
| `cycle_id` not yet available at synthesis time | `synthesizer.synthesize()` accepts `cycle_id: uuid.UUID` as a parameter — Phase 1d passes it in |

---

## Acceptance Criteria

- [ ] `synthesizer.synthesize(items, cycle_id)` returns `list[DigestItem]`
- [ ] Every `DigestItem.narrative` is a non-empty string containing a `Source:` citation
- [ ] Every `DigestItem.source_url` matches a `source_url` from the input `FetchedItem`
- [ ] No more than 5 `DigestItem`s per domain are returned
- [ ] Malformed Claude JSON response → that domain returns `[]`, no crash
- [ ] API error on one domain → other domains still succeed
- [ ] All tests pass
- [ ] `ecc:python-reviewer` passes
- [ ] `ecc:rag-pipeline-reviewer` passes
- [ ] `/frontier-digest-review` passes after 1d wires the full pipeline

---

## ECC Skills to Run

| When | Skill |
|------|-------|
| After implementation | `ecc:python-reviewer` |
| After implementation | `ecc:rag-pipeline-reviewer` |
| After Phase 1d wires the pipeline | `/frontier-digest-review` |
