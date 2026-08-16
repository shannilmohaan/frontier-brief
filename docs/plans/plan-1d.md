# Plan: Phase 1d — Pipeline Wiring & Manual Refresh Endpoint

## Goal
Wire together all Phase 1 services (fetchers, ranker, synthesizer, database) into a complete end-to-end pipeline so clicking Refresh on the frontend fetches real AI news, synthesizes it into narrative digests, persists it to the database, and serves it via API.

## Files to Create

| File | Purpose |
|------|---------|
| `backend/app/services/scheduler/pipeline.py` | Orchestrates the full refresh cycle: fetch → rank → synthesize → persist |
| `backend/tests/api/test_refresh.py` | Tests for POST /api/refresh and GET /api/refresh/{job_id} |
| `backend/tests/api/test_digest.py` | Tests for GET /api/digest/latest |

## Files to Modify

| File | What Changes |
|------|-------------|
| `backend/app/services/ranker.py` | Add public `score_item()` function so pipeline can attach relevance scores to DigestItems |
| `backend/app/api/refresh.py` | Replace placeholder with: concurrent-run guard, DigestCycle creation, BackgroundTask trigger, real status polling via DigestCycle.status |
| `backend/app/api/digest.py` | Replace placeholder with: latest completed DigestCycle query, DigestItem query with optional domain filter |
| `CLAUDE.md` | Update Active Status table |

## Dependencies

- `AsyncSessionLocal` from `app.db.database` — passed as session factory to background task (request-scoped sessions cannot outlive the request)
- All 4 fetchers: `YouTubeFetcher`, `ArxivFetcher`, `TheBatchFetcher`, `HFPapersFetcher`
- `rank_and_cap` from `app.services.ranker`
- `synthesize` from `app.services.synthesis.synthesizer`
- `DigestCycle`, `SourceItem`, `DigestItem` from `app.db.models`
- `settings.refresh_interval_hours`, `settings.max_items_per_domain` from `app.core.config`

## Implementation Order

1. **`ranker.py`** — add `score_item(item)` (depends on nothing)
2. **`pipeline.py`** — full orchestration using all services
3. **`refresh.py`** — concurrent-run guard + BackgroundTask using `run_pipeline`
4. **`digest.py`** — query latest completed cycle + DigestItems
5. **`test_refresh.py`** — auth, 202 + job_id, poll, concurrent guard
6. **`test_digest.py`** — empty state, items returned, domain filter

## Pipeline Logic (pipeline.py)

```
run_pipeline(cycle_id, session_factory)
  └─ _execute_pipeline(cycle_id, session_factory)
       1. Open session → load cycle → set status="running" → commit
       2. asyncio.gather(*[f.fetch() for f in fetchers], return_exceptions=True)
          → log per-fetcher errors, collect successful FetchedItems
       3. Build url→score map: {item.source_url: score_item(item) for item in all_items}
       4. Insert SourceItems → session.flush() to get IDs
       5. rank_and_cap(all_items, max_per_domain=settings.max_items_per_domain)
       6. synthesize(ranked) → list[SynthesizedItem]
       7. For each SynthesizedItem: look up SourceItem by source_url → create DigestItem
          Mark source_item.is_processed = True
       8. cycle.status="completed", items_fetched, items_synthesized, completed_at → commit
  └─ on Exception: open new session → cycle.status="failed", error_message → commit
```

## Refresh Endpoint Logic (refresh.py)

**POST /api/refresh:**
- Validate `X-Refresh-Key` with `hmac.compare_digest`
- Query: is any DigestCycle currently in status "pending" or "running"? If yes → return 202 with its id (idempotent)
- Create `DigestCycle(status="pending", window_start=now-48h, window_end=now)`
- `background_tasks.add_task(run_pipeline, cycle.id, AsyncSessionLocal)`
- Return 202 `{job_id: cycle.id, status: "accepted"}`

**GET /api/refresh/{job_id}:**
- `session.get(DigestCycle, job_id)` → 404 if not found
- Return `{job_id, status}` (maps directly to DigestCycle.status)

## Digest Endpoint Logic (digest.py)

**GET /api/digest/latest?domain=:**
- Query latest `DigestCycle` with `status="completed"` ordered by `completed_at DESC LIMIT 1`
- If none → return `{items: [], domain_filter, cycle_id: null}`
- Query `DigestItem` for that `cycle_id`, optional filter `.where(DigestItem.domain_tags.contains([domain]))`
- Order by `relevance_score DESC`
- Serialize and return

## Risks & Open Questions

- **YouTube API quota**: 5 channels × 50 videos/request = well within 10k unit/day quota
- **Synthesis timeout**: Claude API calls have 30s timeout per domain batch; with 10 domains max, pipeline could take several minutes — BackgroundTask handles this async
- **Frontend 30s polling deadline**: If pipeline takes >30s, frontend shows "taking longer than expected" but the pipeline still completes and the next manual load will show results
- **Concurrent refresh guard**: Returns the existing cycle's job_id rather than 409 — simpler UX

## Acceptance Criteria

- [ ] POST /api/refresh with correct key → 202 + job_id UUID
- [ ] POST /api/refresh with wrong key → 401
- [ ] POST /api/refresh while another is running → 202 + same job_id (idempotent)
- [ ] GET /api/refresh/{job_id} → polls DigestCycle.status correctly
- [ ] GET /api/refresh/{unknown_id} → 404
- [ ] After pipeline completes: GET /api/digest/latest returns items with narratives and source links
- [ ] GET /api/digest/latest?domain=<domain> returns only items with that domain tag
- [ ] Frontend page shows real digest items after clicking Refresh and waiting
- [ ] `/code-review` passed for all new code

## ECC Skills to Run

- After implementation: `ecc:python-reviewer`, `ecc:fastapi-reviewer`, `ecc:security-reviewer`
- After review passes: `/frontier-phase-gate` (all of Phase 1 complete)
