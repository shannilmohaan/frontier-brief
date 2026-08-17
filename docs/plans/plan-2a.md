# Plan: Phase 2a — Full Product Pivot (frontier-ai-specs.md alignment)

## Goal
Transform Frontier Brief from a general AI news aggregator into an **AI Builder Intelligence Platform** — with a new practitioner-focused content taxonomy, richer per-item synthesis fields (Build Impact, Production Readiness, What Changed, Who Should Care), a 9-dimension relevance scoring model, and a fully redesigned frontend that organises content around what a software architect actually wants to know.

---

## Files to Create

| Path | Purpose |
|------|---------|
| `backend/alembic/versions/005_add_builder_intel_fields.py` | Migration: add `build_impact`, `production_readiness`, `what_changed`, `who_should_care` columns to `digest_items` |
| `frontend/src/components/digest/BuildImpactBadge.tsx` | Badge component: 🔥 Very High / High / Medium / Low / Background |
| `frontend/src/components/digest/ProductionReadinessPill.tsx` | Pill: Experimental / Preview / Beta / Production Ready / Enterprise Ready |

---

## Files to Modify

| File | What changes |
|------|-------------|
| `backend/app/services/ranker.py` | Replace `DOMAIN_KEYWORDS` with 8-category spec taxonomy; replace scoring formula with 9-dimension weighted model |
| `backend/app/services/synthesis/prompts.py` | Complete rewrite: new system prompt (AI builder focus), new user prompt requesting `build_impact`, `production_readiness`, `what_changed`, `who_should_care` in addition to existing fields |
| `backend/app/services/synthesis/synthesizer.py` | Add 4 new fields to `SynthesizedItem` dataclass; update `_parse_response` to extract and validate them |
| `backend/app/db/models.py` | Add 4 new nullable columns to `DigestItem` mapped class |
| `backend/app/api/digest.py` | Add 4 new fields to `DigestItemSchema` Pydantic model |
| `backend/app/services/scheduler/pipeline.py` | Pass 4 new fields when constructing `DigestItem` |
| `frontend/src/lib/types.ts` | Add 4 new fields to `DigestItem` TypeScript interface |
| `frontend/src/lib/credibility.ts` | Align credibility labels to spec's source type vocabulary |
| `frontend/src/app/globals.css` | Add CSS tokens for Build Impact color scale and new section styling |
| `frontend/src/app/page.tsx` | New navigation (Today + 7 domain tabs per spec §8); new homepage section order per spec §21; remove `activeTab` video/podcasts filter (now handled via domain tabs) |
| `frontend/src/components/digest/HeroCard.tsx` | Show `build_impact`, `production_readiness`, `what_changed`; update editorial framing to "AI Builder Briefing" |
| `frontend/src/components/digest/DigestCard.tsx` | Replace importance dots + credibility pill with `BuildImpactBadge` + `ProductionReadinessPill`; add `who_should_care` line; add `what_changed` field |
| `frontend/src/components/filters/DomainFilterChips.tsx` | No structural change; domain names update automatically once `DOMAIN_KEYWORDS` changes |

---

## New Content Taxonomy (replaces current 10 domains)

```python
DOMAIN_KEYWORDS = {
    "Agentic AI":       ["agent", "agentic", "autonomous agent", "multi-agent", "mcp", "model context protocol",
                         "tool calling", "tool use", "function calling", "memory", "context engineering",
                         "orchestration", "agent framework", "agent skills", "agent workflow", "self-improving"],
    "AI Architecture":  ["rag", "retrieval augmented", "agentic rag", "workflow pattern", "event-driven",
                         "human-in-the-loop", "integration pattern", "application architecture", "vector database",
                         "embedding", "chunking", "pgvector", "pinecone", "weaviate"],
    "AI Engineering":   ["sdk", "langchain", "llamaindex", "llm api", "prompting", "evaluation", "evals",
                         "observability", "guardrails", "ai security", "tracing", "weave", "braintrust",
                         "context window", "prompt engineering", "structured output"],
    "AI Coding":        ["codex", "claude code", "cursor", "github copilot", "coding agent", "agentic software",
                         "agentic development", "swe-bench", "devin", "ai coder", "automated coding",
                         "ai programming", "ai developer", "vibe coding", "windsurf"],
    "Production AI":    ["deployment", "scalability", "reliability", "cost optimization", "inference cost",
                         "latency", "governance", "monitoring", "enterprise", "production", "mlops",
                         "vllm", "ollama", "triton", "batch inference", "throughput", "security",
                         "compliance", "edge deployment"],
    "Models":           ["gpt-4", "gpt-5", "claude 3", "claude 4", "claude 5", "gemini", "llama",
                         "mistral", "phi-", "qwen", "model release", "new model", "multimodal",
                         "vision model", "reasoning model", "o1", "o3", "thinking model", "context window"],
    "AI Applications":  ["llm application", "enterprise ai", "ai assistant", "ai search", "ai automation",
                         "chatbot", "virtual assistant", "ai product", "copilot"],
    "Industry":         ["funding", "acquisition", "partnership", "open source release", "policy",
                         "regulation", "ai safety", "responsible ai", "research breakthrough"],
}
```

---

## New 9-Dimension Scoring Formula

Per spec §13. Dimensions are approximated from available metadata:

| Dimension | Weight | Signal |
|-----------|--------|--------|
| Application Relevance | 20% | Domain: Agentic AI / AI Coding / Production AI / AI Engineering → high |
| Production Usefulness | 20% | Domain: Production AI → high; Models → medium; Industry → low |
| Learning Value | 15% | content_type: video / blog → high; newsletter → medium |
| Architecture Impact | 15% | Domain: AI Architecture → high |
| Practicality | 10% | Domain: AI Coding / AI Engineering → high |
| Credibility | 10% | `_SOURCE_CREDIBILITY` dict |
| Novelty | 5% | Recency proxy (new = novel) |
| Recency | 3% | Age decay over 7-day window |
| Popularity | 2% | `social_score` |

---

## New Synthesis Fields (added to Claude output)

```json
{
  "source_url": "...",
  "narrative": "2–3 sentences: what happened, factually.",
  "why_it_matters": "1–2 sentences: downstream significance for application developers.",
  "what_changed": "1 sentence: before → after. What is now different.",
  "who_should_care": "Comma-separated roles: e.g. AI architects, software engineers, engineering leaders",
  "build_impact": "Very High | High | Medium | Low | Background",
  "production_readiness": "Experimental | Preview | Beta | Production Ready | Enterprise Ready | N/A",
  "importance": 1–5
}
```

---

## New Navigation (spec §8)

Replace `Today / Videos / Podcasts` tabs with:

```
Today  |  Build  |  Agents  |  Architecture  |  AI Coding  |  Production  |  Tools  |  Learn
```

Tab → domain filter mapping:
- Today → all items (no filter)
- Build → AI Applications
- Agents → Agentic AI
- Architecture → AI Architecture
- AI Coding → AI Coding
- Production → Production AI
- Tools → AI Engineering
- Learn → all, sorted by learning value proxy (videos + newsletters first)

---

## New Homepage Section Order (spec §21)

1. **What Matters Today** — top 5–10 by relevance score (hero card = #1)
2. **AI Coding** — Codex, Claude Code, Cursor, coding agents
3. **Agentic AI** — agents, MCP, orchestration
4. **AI Architecture** — RAG, multi-agent, patterns
5. **Production AI** — security, reliability, cost
6. **Tools Worth Trying** — AI Engineering domain items

---

## Dependencies

- All dependencies already installed (no new packages needed)
- Neon DB: new migration needed before deploy
- Railway: auto-redeploys on push
- Vercel: auto-redeploys on push

---

## Implementation Order

1. `ranker.py` — Replace `DOMAIN_KEYWORDS` and rewrite `_relevance_score` with 9-dimension formula
2. `prompts.py` — Rewrite system + user prompt (new fields, AI builder framing)
3. `synthesizer.py` — Add 4 new fields to `SynthesizedItem`; update `_parse_response`
4. `db/models.py` — Add 4 new mapped columns to `DigestItem`
5. `alembic/versions/005_add_builder_intel_fields.py` — Migration for 4 new columns
6. `digest.py` — Add 4 fields to `DigestItemSchema`
7. `pipeline.py` — Pass new fields when constructing `DigestItem`
8. `types.ts` — Add 4 new fields to frontend interface
9. `BuildImpactBadge.tsx` — New badge component
10. `ProductionReadinessPill.tsx` — New pill component
11. `globals.css` — Add CSS tokens for build impact colors
12. `HeroCard.tsx` — Add new fields display
13. `DigestCard.tsx` — Redesign with new fields
14. `page.tsx` — New navigation, new section layout
15. Commit + push → Railway + Vercel auto-deploy
16. Trigger refresh from UI → verify new fields appear in digest

---

## Risks & Open Questions

- **Claude JSON output size**: 8 fields per item × N items may approach token limits. Mitigation: keep `_MAX_ITEMS_PER_DOMAIN = 5` (already set).
- **Existing DB rows**: rows created before migration will have NULL in new columns — handled gracefully with `| null` types in frontend.
- **Domain reclassification**: existing items in DB will keep old domain tags. New tags only appear after next refresh run.
- **`what_changed` quality**: Claude needs real content context to write a meaningful "before → after" statement. Items with thin summaries will receive empty strings — acceptable.

---

## Acceptance Criteria

- [ ] New taxonomy domains appear in domain filter chips (Agentic AI, AI Architecture, AI Coding, Production AI, etc.)
- [ ] New nav tabs visible: Today / Build / Agents / Architecture / AI Coding / Production / Tools / Learn
- [ ] Each digest card shows Build Impact badge and Production Readiness pill
- [ ] HeroCard shows `what_changed` and `who_should_care` fields
- [ ] Backend synthesis output includes all 8 fields in JSON
- [ ] Migration `005` runs cleanly on Neon (check Railway logs)
- [ ] No TypeScript build errors on Vercel
- [ ] Digest items in AI Coding / Production AI domains outrank general news items

---

## ECC Skills to Run

| When | Skill |
|------|-------|
| After backend changes | `ecc:python-reviewer` |
| After frontend changes | `ecc:react-reviewer` |
| Before pushing | `ecc:security-reviewer` |
| After deploy | `/frontier-ui-check` |
| After deploy + refresh | `/frontier-digest-review` |
