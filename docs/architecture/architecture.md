# Frontier Brief — System Architecture

**Version:** 1.0
**Phase:** 0c
**Date:** 2026-08-15

---

## System Overview

Frontier Brief is a three-tier web application: a Next.js frontend served by Vercel, a FastAPI backend with an embedded scheduler running on Railway, and a PostgreSQL database on Neon. The local machine is used only for writing code — nothing runs locally.

```
┌─────────────────────────────────────────────────────────────┐
│                        USER DEVICES                         │
│              Phone (primary) · Laptop · Any browser         │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   VERCEL (Free tier)                        │
│                  Next.js 14 Frontend                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Digest Page │  │ Filter Chips │  │  DigestCard × N   │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│          robots.txt: Disallow / (no search indexing)        │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API calls (HTTPS)
                          │ CORS: only frontierbrief.vercel.app
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  RAILWAY (Free $5 credit/month)             │
│                   FastAPI Backend                           │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    REST API Layer                    │   │
│  │  GET /api/digest/latest   (open — DB read only)      │   │
│  │  GET /api/digest/latest?domain=X  (open)             │   │
│  │  POST /api/refresh        (protected — REFRESH_KEY)  │   │
│  │  GET /api/refresh/{id}    (open)                     │   │
│  │  GET /health              (open)                     │   │
│  │  Rate limit: 100 req/min per IP (slowapi)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              APScheduler (every 48h)                 │   │
│  │  Triggers the fetch + synthesis pipeline             │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │                 Fetchers Pipeline                    │   │
│  │  ┌────────────┐ ┌────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │  YouTube   │ │ arXiv  │ │The Batch │ │  HF    │  │   │
│  │  │  Data API  │ │  API   │ │   RSS    │ │Papers  │  │   │
│  │  └────────────┘ └────────┘ └──────────┘ └────────┘  │   │
│  │  Each fetcher is isolated — one failure ≠ all fail   │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ raw SourceItems                     │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │           Ranker + Deduplicator                      │   │
│  │  Remove duplicate URLs · Rank by recency + relevance │   │
│  │  Cap: keep top 20 items per domain before synthesis  │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ ranked SourceItems                  │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │           Synthesis Engine (Claude API)              │   │
│  │  Generates 2–4 sentence narrative per item           │   │
│  │  Classifies domain tags · Appends citation           │   │
│  │  Caps output: 5 DigestItems per domain               │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │ DigestItems                         │
└───────────────────────┼─────────────────────────────────────┘
                        │ SQL (asyncpg over TLS)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   NEON (Free tier)                          │
│              Serverless PostgreSQL                          │
│                                                             │
│   digest_cycles · source_items · digest_items              │
│                                                             │
│   Connection pooling: Neon serverless driver               │
│   SSL: required (Neon enforces it)                         │
└─────────────────────────────────────────────────────────────┘

External APIs (called by Railway backend only):
  ├── Anthropic API  (synthesis — once per 48h cycle)
  ├── YouTube Data API v3  (fetcher — quota: 10k units/day)
  ├── arXiv API  (fetcher — free, no key)
  ├── The Batch RSS  (fetcher — free)
  └── Hugging Face Papers  (fetcher — free)
```

---

## Deployment Pipeline

```
┌──────────────────────────────────────────────────────────┐
│  Developer (local machine — code editing only)           │
│                                                          │
│  Claude Code  →  edit files  →  git push origin main    │
└───────────┬──────────────────────────┬───────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────┐      ┌────────────────────────┐
│  Vercel           │      │  Railway               │
│                   │      │                        │
│  Detects push →   │      │  Detects push →        │
│  Build Next.js →  │      │  Install deps →        │
│  Deploy to CDN    │      │  Start FastAPI server  │
│                   │      │  (uvicorn)             │
│  URL: https://    │      │                        │
│  frontierbrief.   │      │  URL: https://         │
│  vercel.app       │      │  api.frontierbrief.    │
│                   │      │  railway.app           │
└───────────────────┘      └────────────────────────┘
            │                          │
            └──────────┬───────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │  Neon PostgreSQL │
            │  (always on —    │
            │  not deployed,   │
            │  just connected) │
            └──────────────────┘
```

No CI/CD pipeline needed for Phase 1 — Vercel and Railway handle deployment automatically on every push to `main`.

---

## Monorepo Structure

```
frontier-brief/                    ← GitHub repository root
├── frontend/                      ← Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           ← Home page (digest view)
│   │   │   ├── layout.tsx         ← Root layout
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── digest/
│   │   │   │   ├── DigestCard.tsx
│   │   │   │   ├── DigestSection.tsx
│   │   │   │   └── SourceLink.tsx
│   │   │   ├── filters/
│   │   │   │   └── DomainFilterChips.tsx
│   │   │   └── ui/
│   │   │       ├── Spinner.tsx
│   │   │       └── EmptyState.tsx
│   │   └── lib/
│   │       ├── api.ts             ← All calls to Railway backend
│   │       └── types.ts           ← Shared TypeScript types
│   ├── public/
│   │   └── robots.txt             ← Disallow: / (no indexing)
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── vercel.json                ← Vercel build config (root dir: frontend)
│
├── backend/                       ← FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── digest.py          ← GET /api/digest/latest
│   │   │   └── refresh.py         ← POST /api/refresh, GET /api/refresh/{id}
│   │   ├── core/
│   │   │   ├── config.py          ← Settings from env vars (pydantic-settings)
│   │   │   ├── security.py        ← REFRESH_KEY validation middleware
│   │   │   └── rate_limit.py      ← slowapi rate limiter setup
│   │   ├── db/
│   │   │   ├── models.py          ← SQLAlchemy ORM models
│   │   │   ├── session.py         ← Async DB session factory
│   │   │   └── migrations/        ← Alembic migration files
│   │   ├── services/
│   │   │   ├── fetchers/
│   │   │   │   ├── base.py        ← BaseFetcher abstract class
│   │   │   │   ├── youtube.py     ← YouTube Data API fetcher
│   │   │   │   ├── arxiv.py       ← arXiv API fetcher
│   │   │   │   ├── the_batch.py   ← The Batch RSS fetcher
│   │   │   │   └── hf_papers.py   ← Hugging Face Papers fetcher
│   │   │   ├── synthesis/
│   │   │   │   ├── client.py      ← Anthropic API client wrapper
│   │   │   │   ├── prompts.py     ← All prompt templates as named constants
│   │   │   │   └── synthesizer.py ← Orchestrates LLM synthesis per item
│   │   │   ├── ranker.py          ← Deduplication and relevance ranking
│   │   │   ├── pipeline.py        ← Orchestrates full fetch→rank→synthesize cycle
│   │   │   └── scheduler.py       ← APScheduler job (every 48h)
│   │   └── main.py                ← FastAPI app, CORS, lifespan (starts scheduler)
│   ├── tests/
│   │   ├── fetchers/
│   │   ├── synthesis/
│   │   └── api/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── railway.toml               ← Railway build + start command config
│
├── docs/
│   ├── prd/
│   │   └── prd-phase-1.md
│   ├── plans/
│   │   └── plan-0c.md
│   └── architecture/
│       ├── architecture.md        ← This file
│       ├── adr-001-hosting.md
│       └── adr-002-security.md
│
├── ideas_v2.md
└── CLAUDE.md
```

---

## Component Responsibilities

### Frontend (Vercel — Next.js)

| Component | Responsibility |
|-----------|---------------|
| `app/page.tsx` | Fetches digest from backend on load; renders filter chips + digest cards |
| `DomainFilterChips` | Horizontal scrollable chip bar; filters digest items client-side |
| `DigestCard` | Renders one digest item: domain tag, content type icon, narrative, source link |
| `SourceLink` | Tappable link that opens the original source in a new tab |
| `lib/api.ts` | All `fetch()` calls to the Railway backend; typed responses |
| `public/robots.txt` | `User-agent: *` / `Disallow: /` — prevents search engine indexing |

The frontend is a **static read** of the database via the API. It makes no LLM calls. It costs nothing to serve page views beyond bandwidth.

### Backend (Railway — FastAPI)

| Component | Responsibility |
|-----------|---------------|
| `main.py` | App entry point; registers CORS, rate limiter, router; starts scheduler on startup |
| `api/digest.py` | `GET /api/digest/latest` — reads from DB, returns cached digest; open endpoint |
| `api/refresh.py` | `POST /api/refresh` — protected; triggers pipeline; `GET` polls status |
| `core/config.py` | Reads all env vars via pydantic-settings; fails fast on missing required vars |
| `core/security.py` | Validates `X-Refresh-Key` header on POST /refresh only |
| `core/rate_limit.py` | 100 req/min per IP on all endpoints via slowapi + Redis (or in-memory for Phase 1) |
| `services/pipeline.py` | Orchestrates: fetch → rank/dedup → synthesize → save to DB |
| `services/scheduler.py` | APScheduler job: runs pipeline every 48h; checks on startup if overdue |
| `services/fetchers/` | One fetcher per source; all extend BaseFetcher; isolated failure handling |
| `services/synthesis/` | Calls Anthropic API; one call per SourceItem; writes DigestItems |
| `services/ranker.py` | Dedup by URL; rank by recency + topic match; cap at 20 pre-synthesis |

### Database (Neon — PostgreSQL)

Three tables — defined in PRD Phase 1. All writes happen from Railway. Vercel reads via Railway API — never touches the DB directly.

---

## Data Flow — Full Refresh Cycle

```
APScheduler fires (every 48h)
        │
        ▼
pipeline.py: create DigestCycle(status=in_progress)
        │
        ├── youtube.py: fetch last 48h videos from 5 channels
        ├── arxiv.py:   fetch last 48h papers (cs.AI, cs.LG, cs.CL)
        ├── the_batch.py: fetch last 48h articles from RSS
        └── hf_papers.py: fetch last 48h highlighted papers
        │
        │ (each runs independently; failures are logged + skipped)
        │
        ▼
ranker.py:
  - Remove duplicate URLs
  - Remove near-duplicate titles
  - Score by: (recency weight × 0.6) + (topic match weight × 0.4)
  - Cap: keep top 20 items per domain
        │
        ▼
synthesizer.py (per item, in batches):
  - Build prompt: title + raw_content + domain context
  - Call claude-sonnet-5: generate 2–4 sentence narrative
  - Classify/confirm domain tags
  - Append "Source: [Name](url)" citation
  - Save as DigestItem
  - Cap: keep top 5 DigestItems per domain
        │
        ▼
pipeline.py: mark DigestCycle(status=completed)
        │
        ▼
Frontend: next GET /api/digest/latest returns the new cycle
```

---

## Frontend → Backend Communication

```
Vercel frontend
  └── lib/api.ts
        │
        │  GET https://api.frontierbrief.railway.app/api/digest/latest
        │  GET https://api.frontierbrief.railway.app/api/digest/latest?domain=Agentic+AI
        │  POST https://api.frontierbrief.railway.app/api/refresh
        │       Header: X-Refresh-Key: {NEXT_PUBLIC_REFRESH_KEY}
        │  GET https://api.frontierbrief.railway.app/api/refresh/{id}
        │
        ▼
Railway FastAPI backend
  └── CORS: Allow-Origin: https://frontierbrief.vercel.app only
```

`NEXT_PUBLIC_REFRESH_KEY` is set in Vercel environment variables. It is sent in the `X-Refresh-Key` header on refresh calls only. All other endpoints are open.

---

## Security Architecture

### Threat Model (Phase 1)

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Someone discovers the URL and reads the digest | High | None — it's public AI news | Acceptable; no mitigation needed |
| Someone spams POST /refresh → runaway Anthropic API bills | Medium | High | Protected by `X-Refresh-Key` header |
| Search engine indexes the site → organic traffic | Medium | Low (bandwidth) | `robots.txt: Disallow: /` |
| DDoS or high traffic → Railway credit exhausted | Low | Service stops (not a bill) | Free tier hard cap; rate limiting |
| Secrets leaked in code | Low | High | All secrets in env vars only; `.env` in `.gitignore` |

### Implementation

```python
# Only the /refresh endpoint checks the key
# All GET endpoints are open

@router.post("/api/refresh")
async def trigger_refresh(
    request: Request,
    key: str = Header(alias="X-Refresh-Key")
):
    if key != settings.REFRESH_KEY:
        raise HTTPException(status_code=401, detail="Invalid key")
    # ... start pipeline
```

### Rate Limiting

All endpoints: **100 requests per minute per IP** via `slowapi`.
This stops casual abuse without affecting legitimate single-user use.

### What This Costs if Abused

- GET /digest/latest: reads DB → ~0.1ms compute, ~2KB response. 1M requests = ~$0 on Railway free tier (capped by credit anyway).
- POST /refresh: protected by key → effectively zero unauthorized calls.
- Anthropic API: only called by the scheduler (every 48h) and authorized refreshes → fixed cost.

---

## Environment Variables

All secrets live in hosting platform dashboards — never in code or committed files.

### Railway (Backend)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname?ssl=require

# LLM
ANTHROPIC_API_KEY=sk-ant-...

# Security
REFRESH_KEY=generate-a-long-random-string-here

# Sources
YOUTUBE_API_KEY=AIza...

# App config
MAX_ITEMS_PER_DOMAIN=5
REFRESH_INTERVAL_HOURS=48
ENVIRONMENT=production
```

### Vercel (Frontend)

```bash
# Backend URL (Railway)
NEXT_PUBLIC_API_URL=https://api.frontierbrief.railway.app

# Refresh key (same value as Railway REFRESH_KEY)
NEXT_PUBLIC_REFRESH_KEY=generate-a-long-random-string-here
```

### `.env.example` (committed to GitHub — no real values)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname?ssl=require
ANTHROPIC_API_KEY=
REFRESH_KEY=
YOUTUBE_API_KEY=
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_REFRESH_KEY=
MAX_ITEMS_PER_DOMAIN=5
REFRESH_INTERVAL_HOURS=48
ENVIRONMENT=development
```

---

## Cost Ceiling Strategy

**Principle:** Use only free tiers with hard spending limits. Services stop when limits are hit — they do not charge overages.

| Service | Plan | Monthly Cost | Limit Behavior |
|---------|------|-------------|----------------|
| Vercel | Free | $0 | Stops serving at 100GB bandwidth — never charges |
| Railway | Free ($5 credit) | $0–$5 | Service stops when credit runs out — no auto-charge |
| Neon | Free | $0 | Stops connections at 0.5GB storage — never charges |
| Anthropic | Pay-per-use | ~$0.10–$0.50 | Set a usage limit in Anthropic dashboard |
| YouTube API | Free quota | $0 | 10k units/day hard quota — returns errors, no charge |
| **Total** | | **< $1/month** | All services self-limit |

**Anthropic usage limit:** Set a monthly spend cap of $5 in the Anthropic Console at `console.anthropic.com → Settings → Limits`. This is the only service that charges per-call rather than stopping.

---

## Railway Configuration

```toml
# backend/railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

## Vercel Configuration

```json
// frontend/vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

---

## Open Items Before Phase 1 Starts

| Item | Blocking? | Action needed |
|------|-----------|---------------|
| Confirm The Batch RSS feed URL | Yes — needed for fetcher | Verify at deeplearning.ai before 1a |
| Confirm Hugging Face Papers feed URL | Yes — needed for fetcher | Verify feed endpoint before 1a |
| YouTube API quota estimate | Yes — needed for fetcher design | Estimate: 5 channels × 50 units/search × 1 search/48h ≈ 250 units/refresh — well within 10k/day limit |
| Anthropic spend limit | Yes — needed before synthesis runs | Set $5/month cap in Anthropic Console |
| Generate REFRESH_KEY | Yes — needed before deploy | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| Register domain (optional) | No | frontierbriefing.com or similar — can use Vercel subdomain for Phase 1 |

---

*Architecture document for Frontier Brief Phase 0c. Reviewed and approved before Phase 0d begins.*
