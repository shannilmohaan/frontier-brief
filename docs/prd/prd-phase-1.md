# Frontier Brief — PRD Phase 1: MVP

**Version:** 1.0
**Date:** 2026-08-15
**Status:** Draft — awaiting user approval
**Author:** Claude Code + Shanir

---

## Overview

Phase 1 delivers a working, single-user Frontier Brief application. It fetches content from four AI sources (YouTube, arXiv, The Batch, Hugging Face Papers), synthesizes the top items into short narrative digests using the Claude API, and displays them in a mobile-first web UI with domain-based filtering. Refresh is triggered manually. No authentication, no scheduler — just the core loop working end to end.

---

## Goals

- Prove the core value: a curated, synthesized AI digest is more useful than raw feeds
- Get real content on screen that the user can actually read and click through
- Establish the full technical stack (monorepo, Railway backend, Neon DB, Vercel frontend)
- Validate the narrative digest format and mobile UI before expanding scope

---

## Out of Scope — Phase 1

The following are explicitly deferred. Do not build these in Phase 1:

- Automated scheduler (every 48h refresh) → Phase 2
- Thumbs-up / thumbs-down feedback system → Phase 2
- Additional sources beyond the 4 listed below → Phase 2
- Email / push notifications → Phase 2
- User authentication → Phase 4
- Preference learning / personalization → Phase 3
- Production deployment (Vercel + Railway prod) → end of Phase 2
- LinkedIn, Reddit, X.com, GitHub, Substacks → Phase 2+

---

## Infrastructure Decisions (Phase 0d, resolved)

**Principle:** The local machine is for writing code only. Nothing runs locally — not the frontend, not the backend, not the database. The app is accessible from any device, anywhere, at all times.

| Component | Choice | Cost | Rationale |
|-----------|--------|------|-----------|
| Repo structure | Monorepo on GitHub | Free | Single repo: `frontend/` + `backend/` + `docs/` |
| Frontend hosting | Vercel | Free | Perfect for Next.js; auto-deploys on every git push; accessible from any device |
| Backend hosting | Railway | Free ($5 credit/month) | Hosts FastAPI + APScheduler; always-on; auto-deploys from GitHub |
| Database | Neon (serverless PostgreSQL) | Free (0.5GB) | Serverless PostgreSQL; no server to manage; sufficient for Phase 1–3 digest data |
| **Total** | | **$0–$5/month** | Railway free credit covers a lightweight FastAPI service |

**Development workflow:**
1. Write and edit code locally with Claude Code
2. `git push` to GitHub
3. Vercel auto-deploys the Next.js frontend
4. Railway auto-deploys the FastAPI backend
5. Test via the live Vercel and Railway URLs — no localhost needed

**Why Neon over Supabase (Phase 1–3):**
Neon is simpler — pure PostgreSQL, less overhead. Supabase becomes the better choice in Phase 4 when multi-user auth is needed (Supabase has auth built in). The migration from Neon to Supabase is straightforward when that time comes.

**Why Railway over Render:**
Render's free tier spins down services after 15 minutes of inactivity — a cold start would delay the first API response by 30–60 seconds. Railway's free credit keeps the service always-on.

---

## User Stories

### S1 — View the Latest Digest
**As a user, I want to see the latest AI digest when I open Frontier Brief,**
so that I can quickly catch up on what happened in the past 48 hours.

Acceptance criteria:
- [ ] The home page loads the most recent digest cycle's items
- [ ] Items are grouped by domain
- [ ] Each item shows: domain tag, narrative summary (2–4 sentences), source name, and a direct link to the original
- [ ] Page loads in under 2 seconds on a mobile connection

### S2 — Filter by Domain
**As a user, I want to tap a domain chip to see only items from that topic area,**
so that I can focus on what interests me most in a given session.

Acceptance criteria:
- [ ] A row of filter chips is visible at the top of the page, one per domain
- [ ] Tapping a chip filters the digest to show only items tagged with that domain
- [ ] An "All" chip shows the full digest
- [ ] The active chip is visually distinct
- [ ] On mobile, the chip row scrolls horizontally if all chips don't fit on screen

### S3 — Click Through to the Original Source
**As a user, I want to tap the source link on any digest item to open the original content,**
so that I can read the full article, watch the full video, or read the full paper when something interests me.

Acceptance criteria:
- [ ] Every digest item has a "Source: [Name] →" link
- [ ] The link opens the exact original content (specific video, paper, or article — not a homepage)
- [ ] The link opens in a new tab / browser on mobile
- [ ] The tap target is at least 44×44px

### S4 — Trigger a Manual Refresh
**As a user, I want to trigger a fresh content fetch when I want updated content,**
so that I can get the latest items without waiting for a scheduled job (which doesn't exist yet in Phase 1).

Acceptance criteria:
- [ ] A "Refresh" button is visible on the page (not prominent — secondary action)
- [ ] Tapping Refresh triggers a background fetch + synthesis job
- [ ] The UI shows a loading state while the refresh is running
- [ ] When complete, the digest updates with new items
- [ ] If a refresh fails, an error message is shown — not a silent failure

---

## Functional Requirements

### FR1 — Data Pipeline

**FR1.1 — Source Fetchers**
Each source has its own fetcher module in `backend/app/services/fetchers/`. All fetchers implement the `BaseFetcher` interface.

**FR1.2 — Required Fields per Fetched Item**
Every fetcher must return items with these fields:
- `title: str` — title of the video, paper, or article
- `raw_content: str` — description, abstract, or excerpt (≥100 chars, ≤2000 chars)
- `source_name: str` — human-readable source name (e.g., "Yannic Kilcher", "arXiv", "The Batch")
- `source_url: str` — direct URL to the specific item (not the homepage)
- `content_type: Enum["video", "paper", "newsletter"]`
- `published_at: datetime` — when the content was originally published
- `domain_tags: list[str]` — one or more tags from the canonical domain list

**FR1.3 — Source: YouTube**
- API: YouTube Data API v3 (requires `YOUTUBE_API_KEY`)
- Channels to monitor (Phase 1 list):
  - Yannic Kilcher (`@YannicKilcher`)
  - Andrej Karpathy (`@AndrejKarpathy`)
  - Two Minute Papers (`@TwoMinutePapers`)
  - AI Explained (`@aiexplained-official`)
  - Sam Witteveen (`@samwitteveenai`)
- Fetch: videos published in the last 48 hours from each channel
- Fields: title, description (first 500 chars), channel name, video URL, published date
- Rate limit: YouTube Data API has a 10,000 unit/day quota — use search.list sparingly

**FR1.4 — Source: arXiv**
- API: arXiv API (free, no key required)
- Query: categories `cs.AI`, `cs.LG`, `cs.CL` + keyword filter for topics of interest
- Fetch: papers submitted in the last 48 hours
- Fields: title, abstract (first 600 chars), authors, arXiv paper URL
- Domain tags: derived from abstract content using LLM classification

**FR1.5 — Source: The Batch (deeplearning.ai)**
- API: RSS feed
- Feed URL: `https://www.deeplearning.ai/the-batch/` (confirm RSS URL before implementation)
- Fetch: articles published in the last 48 hours
- Fields: title, excerpt, article URL, published date
- Note: The Batch publishes weekly — may return 0 items between issues; handle gracefully

**FR1.6 — Source: Hugging Face Papers**
- API: Hugging Face daily papers feed (confirm endpoint before implementation)
- Fetch: papers highlighted in the last 48 hours
- Fields: paper title, abstract excerpt, Hugging Face paper URL, published date

**FR1.7 — Failure Isolation**
If one source fetcher fails (network error, rate limit, empty response), the pipeline must:
- Log the error with source name and reason
- Continue processing the remaining sources
- Never crash the entire pipeline because one source failed

**FR1.8 — Deduplication**
Before synthesis, deduplicate items:
- Remove exact URL duplicates (same paper from arXiv and Hugging Face)
- Flag near-duplicates (same paper title, different URL) — keep the more informative one

---

### FR2 — Synthesis Engine

**FR2.1 — LLM Digest Generation**
Use the Claude API (`claude-sonnet-5` model) to synthesize each fetched item into a digest entry.

**FR2.2 — Narrative Format**
Each synthesized item must be:
- 2–4 sentences in length
- Written in narrative prose (no bullet points, no headers within the item)
- Tone: knowledgeable colleague briefing you — specific, clear, not promotional
- Must explain WHY the development matters, not just what it is
- Must not use: "groundbreaking", "revolutionary", "game-changing", "exciting"

**FR2.3 — Citation Format**
Every digest item ends with:
```
Source: [Source Name](direct_url_to_original_content)
```
This is mandatory. An item without a citation is a bug.

**FR2.4 — Domain Classification**
If a fetched item does not have domain tags, use the LLM to classify it into one or more domains from the canonical list:
- Agentic AI
- New Model Capabilities
- Context Management
- Token Economics
- Tool Use & Function Calling
- AI Coding Agents
- Reasoning & Planning
- Agent Memory & Persistence
- Applied AI Engineering
- AI Research

**FR2.5 — Volume Cap**
After synthesis, rank all items by relevance (recency + topic match). Keep the top 5 items per domain per digest cycle. Discard the rest.

**FR2.6 — Synthesis Prompt**
The synthesis prompt lives in `backend/app/services/synthesis/prompts.py` as a named constant — not hardcoded in the synthesis function. This allows iteration without touching logic.

---

### FR3 — API Endpoints

**FR3.1 — Get Latest Digest**
```
GET /api/digest/latest
GET /api/digest/latest?domain={domain_slug}

Response 200:
{
  "cycle_id": "uuid",
  "refreshed_at": "2026-08-15T06:00:00Z",
  "window_hours": 48,
  "domains": ["Agentic AI", "New Models", ...],
  "items": [
    {
      "id": "uuid",
      "domain_tags": ["Agentic AI"],
      "title": "...",
      "narrative": "2-4 sentence narrative...",
      "source_name": "Yannic Kilcher",
      "source_url": "https://youtube.com/watch?v=...",
      "content_type": "video",
      "published_at": "2026-08-14T12:00:00Z"
    }
  ],
  "total_items": 23
}

Response 404:
{ "detail": "No digest available yet. Trigger a refresh first." }
```

**FR3.2 — Trigger Manual Refresh**
```
POST /api/refresh

Response 202:
{
  "cycle_id": "uuid",
  "status": "started",
  "message": "Refresh started. Poll /api/refresh/{cycle_id} for status."
}
```

**FR3.3 — Refresh Status**
```
GET /api/refresh/{cycle_id}

Response 200:
{
  "cycle_id": "uuid",
  "status": "in_progress" | "completed" | "failed",
  "started_at": "...",
  "completed_at": "..." | null,
  "items_fetched": 47,
  "items_synthesized": 23,
  "error": null | "error message if failed"
}
```

**FR3.4 — Health Check**
```
GET /health

Response 200:
{ "status": "ok", "version": "1.0.0" }
```

---

### FR4 — Web UI

**FR4.1 — Page Structure**
```
[Header: "Frontier Brief" | last refreshed timestamp]
[Domain Filter Chips: All | Agentic AI | New Models | ...]
[Digest Items: card list]
[Refresh Button: secondary, bottom or top-right]
```

**FR4.2 — Digest Card**
Each card contains:
- Domain tag pill (small, colored by domain)
- Content type icon (▶ video, 📄 paper, 📰 newsletter)
- Source name (small, muted)
- Narrative text (main body — 2–4 sentences)
- "Source: [Name] →" link (tappable, opens in new tab)

**FR4.3 — Domain Filter Chips**
- Horizontal scrollable row on mobile
- "All" chip selected by default
- Selecting a chip filters the visible cards instantly (client-side — no API call needed if all items are already loaded)
- One chip active at a time

**FR4.4 — Refresh Button**
- Label: "Refresh digest"
- Shows loading spinner while refresh is in progress
- Shows "Last refreshed: X minutes ago" when idle
- On error: shows "Refresh failed — try again"

**FR4.5 — Empty State**
If no digest is available: show a clear message and a prominent Refresh button.

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Mobile page load (LCP) | < 2 seconds on a 4G connection |
| Desktop page load | < 1 second |
| Refresh job duration | < 3 minutes end to end for all 4 sources |
| API response time (`GET /api/digest/latest`) | < 500ms |
| Fetcher failure isolation | Failure of 1 source must not affect others |
| Mobile viewport | Works correctly at 375px width (iPhone SE) |
| Tap targets | Minimum 44×44px for all interactive elements |
| Citations | 100% of digest items must have a source link |

---

## Data Models

### `DigestCycle`
```sql
CREATE TABLE digest_cycles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status      VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    -- values: 'in_progress', 'completed', 'failed'
  window_start TIMESTAMPTZ NOT NULL,
  window_end   TIMESTAMPTZ NOT NULL,
  started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  items_fetched    INTEGER DEFAULT 0,
  items_synthesized INTEGER DEFAULT 0,
  error_message TEXT
);
```

### `SourceItem`
```sql
CREATE TABLE source_items (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id     UUID REFERENCES digest_cycles(id),
  source_name  VARCHAR(100) NOT NULL,
  source_url   TEXT NOT NULL UNIQUE,
  title        TEXT NOT NULL,
  raw_content  TEXT NOT NULL,
  content_type VARCHAR(20) NOT NULL,
    -- values: 'video', 'paper', 'newsletter'
  domain_tags  TEXT[] NOT NULL DEFAULT '{}',
  published_at TIMESTAMPTZ NOT NULL,
  fetched_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_processed BOOLEAN NOT NULL DEFAULT false
);
```

### `DigestItem`
```sql
CREATE TABLE digest_items (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id       UUID REFERENCES digest_cycles(id),
  source_item_id UUID REFERENCES source_items(id),
  narrative      TEXT NOT NULL,
  source_name    VARCHAR(100) NOT NULL,
  source_url     TEXT NOT NULL,
  content_type   VARCHAR(20) NOT NULL,
  domain_tags    TEXT[] NOT NULL DEFAULT '{}',
  relevance_score FLOAT DEFAULT 0.0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Source Requirements Summary

| Source | Auth needed | Format | Cadence | Notes |
|--------|-------------|--------|---------|-------|
| YouTube | `YOUTUBE_API_KEY` | Data API v3 | Per channel, last 48h | 10k unit/day quota |
| arXiv | None | Atom feed / REST API | Last 48h | Free, no key |
| The Batch | None | RSS | Last 48h | Weekly — may return 0 items |
| Hugging Face Papers | None | RSS / API | Last 48h | Daily — confirm feed URL |

---

## Digest Quality Requirements

From `CLAUDE.md` — all enforced by `/frontier-digest-review`:

- Narrative: 2–4 sentences, prose (no bullets), collegial tone
- Citation: every item has `Source: [Name](url)` — mandatory
- URL: must link to the specific item, not a homepage
- Volume: max 5 items per domain per cycle (Phase 1)
- Age: no items older than 48 hours
- Duplicates: no two items covering the same topic in one cycle

---

## Dependencies

| Dependency | Type | Notes |
|-----------|------|-------|
| Anthropic API key | External API | Required for synthesis (FR2.1) |
| YouTube Data API key | External API | Required for YouTube fetcher (FR1.3) |
| GitHub account | Source control | Push triggers auto-deploy to Vercel + Railway |
| Neon account | Hosted DB | Free tier; connection string in Railway env vars |
| Railway account | Backend hosting | Free $5 credit/month; auto-deploys from GitHub |
| Vercel account | Frontend hosting | Free tier; auto-deploys from GitHub |
| arXiv API | External API | No key needed |
| The Batch RSS | External feed | Confirm feed URL before 1a |
| Hugging Face Papers | External feed | Confirm endpoint before 1a |

---

## Open Questions

- [ ] Confirm The Batch RSS feed URL (may need to find via page source)
- [ ] Confirm Hugging Face Papers feed URL / API endpoint
- [ ] YouTube API quota strategy — 5 channels × search queries; estimate units needed per refresh
- [ ] Domain color scheme for filter chips — assign one color per domain
- [ ] Font and color palette for UI (to be asked in Preference Gate 1c)

---

## Definition of Done — Phase 1

Code:
- [ ] All 4 source fetchers implemented and tested
- [ ] Synthesis engine generates narrative digests with citations
- [ ] Volume cap (5 items/domain) enforced
- [ ] All 4 API endpoints return correct responses
- [ ] `GET /health` returns `{"status": "ok"}`

Quality:
- [ ] `/frontier-digest-review` passed (citations, narrative, volume)
- [ ] `/frontier-ui-check` passed (375px mobile layout, tap targets, filter chips)
- [ ] ECC `/code-review` passed on all new files
- [ ] ECC `ecc:python-reviewer` passed on backend
- [ ] ECC `ecc:react-reviewer` passed on frontend
- [ ] ECC `ecc:silent-failure-hunter` passed (fetcher failures handled)

Functional verification:
- [ ] User can open the app on a real mobile phone and read the digest
- [ ] User can tap a domain chip and see only that domain's items
- [ ] User can tap a source link and open the original content
- [ ] User can trigger a refresh and see new content appear
- [ ] If one source is down, the rest still work

Infrastructure:
- [ ] Backend deployed to Railway (dev environment)
- [ ] Frontend deployed to Vercel (preview)
- [ ] Neon DB provisioned and connected
- [ ] `.env.example` documents all required variables
- [ ] No secrets in any committed file

---

*PRD Phase 1 — Frontier Brief. Approved by user before Phase 1 implementation begins.*
