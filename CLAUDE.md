# Frontier Brief — CLAUDE.md

**Frontier Brief** is a personal AI news aggregator that monitors the AI ecosystem across multiple platforms, synthesizes the top developments into short narrative digests every two days, and surfaces them filtered by domain — designed mobile-first for a user who travels frequently.

> **Product vision:** Always read `ideas_v2.md` before making any product or feature decisions. It is the source of truth. This file is the operational guide for how to build it.

---

## Active Status

| Field | Value |
|-------|-------|
| **Current Phase** | Phase 1 — MVP |
| **Active Sub-phase** | 1b — Synthesis engine (in progress) |
| **Next Action** | Run `ecc:python-reviewer` + `ecc:rag-pipeline-reviewer`, then commit and push |

> **Update this table at the start of every session and whenever a sub-phase completes.**

---

## Non-Negotiables

These rules are absolute. Never deviate from them.

1. **No code before a plan** — every sub-phase begins with `/frontier-plan`. No exceptions.
2. **No sub-phase starts without user confirmation** — always run the Preference Gate and wait for explicit approval before writing any code.
3. **Every digest item must have a citation** — source name + direct link to the original content. A summary without a source link is a bug, not a feature.
4. **Mobile-first always** — after any UI change, run `/frontier-ui-check`. The 375px viewport is the baseline.
5. **Volume discipline** — the digest shows 5–10 items per domain per refresh cycle. Never more. The project exists to eliminate noise, not recreate it.
6. **Code review every time** — run ECC `/code-review` after every implementation. No code is done until it has been reviewed.
7. **Ask before deciding** — whenever there is a product or design decision to make, ask the user. Do not assume. Use `AskUserQuestion` when choices are meaningful.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.12 + FastAPI |
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Database | PostgreSQL 16 |
| Vector store | pgvector (for semantic deduplication and ranking) |
| Task scheduler | APScheduler (simple) → Celery + Redis (if complexity grows) |
| LLM (synthesis) | Claude API — `claude-sonnet-5` for digest generation |
| Auth (Phase 4) | NextAuth.js |
| Dev environment | Docker Compose |
| Database | Neon (serverless PostgreSQL, free tier — 0.5GB, enough for Phase 1–3) |
| Hosting — frontend | Vercel (free tier — auto-deploys from GitHub on every push) |
| Hosting — backend | Railway (free $5 credit/month — enough for lightweight FastAPI + scheduler) |
| Local machine role | Write and edit code only. Nothing runs locally. |
| Dev workflow | Push to GitHub → Vercel and Railway auto-deploy → test via live URLs |
| Estimated monthly cost | $0–$5/month total |

> Tech stack decisions are final from Phase 0c. Do not change a technology without running `/frontier-plan` and getting user approval.

---

## Target Project Structure

```
frontier-brief/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers (digest, sources, feedback)
│   │   ├── core/             # Settings, config, logging
│   │   ├── db/               # SQLAlchemy models, migrations (Alembic)
│   │   ├── services/
│   │   │   ├── fetchers/     # One file per source type (youtube.py, arxiv.py, etc.)
│   │   │   ├── synthesis/    # LLM digest generation (claude_client.py, prompt templates)
│   │   │   ├── scheduler/    # APScheduler refresh job
│   │   │   └── ranker.py     # Relevance ranking and deduplication
│   │   └── main.py
│   ├── tests/
│   │   ├── fetchers/         # One test file per fetcher
│   │   ├── synthesis/
│   │   └── api/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/
│   │   │   ├── digest/       # DigestCard, DigestSection, SourceLink
│   │   │   ├── filters/      # DomainFilterChips (mobile horizontal scroll)
│   │   │   └── ui/           # Shared primitives
│   │   └── lib/
│   │       ├── api.ts        # API client for FastAPI backend
│   │       └── types.ts      # Shared TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
├── docs/
│   ├── prd/                  # PRD documents: prd-phase-0.md, prd-phase-1.md, etc.
│   ├── architecture/         # Architecture decision records (ADRs)
│   └── plans/                # Sub-phase plans: plan-1a.md, plan-1b.md, etc.
├── .claude/
│   └── skills/               # Project-specific Claude Code skills
├── docker-compose.yml
├── .env.example
├── ideas_v2.md               # Product vision (source of truth)
└── CLAUDE.md                 # This file
```

---

## ECC Skills Reference

Always use ECC skills at the right stage. Do not skip these.

| When | ECC Skill | What it does |
|------|-----------|-------------|
| Before any new sub-phase | `ecc:planner` or `/plan` | Sprint-level plan for the sub-phase |
| Writing a PRD | `/plan-prd` | Formal Product Requirements Document |
| Architecture design | `ecc:architect` or `/blueprint` | System architecture before code |
| Project scaffold | `/project-init` | Set up folder structure, tooling, CI |
| Each feature | `/feature-dev` or `ecc:orch-build-mvp` | Implement one feature at a time |
| After every code change | `/code-review` or `ecc:code-reviewer` | Review for correctness and quality |
| Python code review | `ecc:python-reviewer` | Python-specific review |
| React/Next.js review | `ecc:react-reviewer` | Frontend-specific review |
| FastAPI review | `ecc:fastapi-reviewer` | API design and async correctness |
| Before any deploy | `/security-scan` or `ecc:security-reviewer` | Catch secrets, injections, misconfigs |
| RAG / retrieval work | `ecc:rag-pipeline-reviewer` | Review retrieval and ranking logic |
| ML pipeline | `ecc:mle-reviewer` | Review LLM pipeline and eval coverage |
| Cleanup after features | `/refactor-clean` or `ecc:code-simplifier` | Remove dead code, simplify |
| Database schema | `ecc:database-reviewer` | SQL and migration review |
| Accessibility | `ecc:a11y-architect` | WCAG compliance check |
| Performance | `ecc:performance-optimizer` | Bottleneck analysis |

---

## Custom Project Skills

These skills are specific to Frontier Brief. Invoke them at the stages listed below.

| Skill | When to Invoke | File |
|-------|---------------|------|
| `/frontier-plan` | Before every sub-phase | `.claude/skills/frontier-plan/SKILL.md` |
| `/frontier-prd` | Phase 0b and before each new phase | `.claude/skills/frontier-prd/SKILL.md` |
| `/frontier-source-add` | When adding any new data source | `.claude/skills/frontier-source-add/SKILL.md` |
| `/frontier-digest-review` | After any synthesis change | `.claude/skills/frontier-digest-review/SKILL.md` |
| `/frontier-ui-check` | After any frontend change | `.claude/skills/frontier-ui-check/SKILL.md` |
| `/frontier-phase-gate` | Before moving to the next phase | `.claude/skills/frontier-phase-gate/SKILL.md` |
| `/frontier-deploy` | Before any production deployment | `.claude/skills/frontier-deploy/SKILL.md` |

---

## Phase Guide

Each phase has a **Preference Gate** — a required set of questions to ask the user before any work begins. Never skip a gate.

---

### Phase 0 — Planning & Architecture
> No code written in this phase. Planning and scaffolding only.

**Sub-phases:**
- `0a` ✅ Requirements finalized (`ideas_v2.md`)
- `0b` ✅ PRD written → `docs/prd/prd-phase-1.md`
- `0c` ✅ Architecture designed → `docs/architecture/architecture.md` + ADR-001 + ADR-002
- `0d` Project scaffold → use ECC `/project-init`

**Preference Gate 0 — Ask before 0b:**
```
1. Review the 10 topics of interest in ideas_v2.md — any to add or remove?
2. Confirm tech stack: Python/FastAPI + Next.js + PostgreSQL — any changes?
3. Monorepo (single repo for frontend + backend) or separate repos?
4. Have you registered a domain? (e.g., frontierbriefing.com, getfrontierbrief.com)
5. Docker Compose for local dev — are you comfortable with Docker?
```

**Definition of Done:**
- [ ] PRD written and approved by user
- [ ] Architecture document in `docs/architecture/`
- [ ] Project scaffolded, `docker-compose up` works
- [ ] `.env.example` created with all required variables documented

---

### Phase 1 — MVP (Single User, No Auth)

**Sub-phases:**
- `1a` Data pipeline — 2–3 sources only
- `1b` Synthesis engine — Claude API → narrative digest
- `1c` Web UI — mobile-first, digest cards, domain filter chips
- `1d` Manual refresh endpoint (no scheduler yet)

**Preference Gate 1 — Ask before 1a:**
```
1. Which 2–3 sources should we implement first?
   Recommended: YouTube RSS + arXiv + The Batch newsletter
   (YouTube is highest priority per ideas_v2.md)
2. How many digest items per domain should Phase 1 show? (Recommended: 5)
3. What time window should the digest cover? (Recommended: last 48 hours)
4. Any UI reference sites or apps you like the look of?
5. Should the digest card show: title + 2–3 sentence summary + source link?
   Or do you want something different?
```

**Preference Gate 1c — Ask before UI work:**
```
1. Color scheme preference? (dark mode, light mode, or system default?)
2. Card style: minimal flat cards, or cards with subtle borders/shadows?
3. Should the domain filter chips be at the top of the page or in a sidebar?
   (For mobile, horizontal scroll chips at top is recommended.)
4. Font preference: modern sans-serif (clean) or something with more character?
```

**ECC Skills to run per sub-phase:**
- Before 1a: `/frontier-plan` → ECC `ecc:planner`
- Implement 1a: ECC `/feature-dev` → `ecc:python-reviewer`
- Before 1b: `/frontier-plan` → ECC `ecc:planner`
- Implement 1b: ECC `/feature-dev` → `ecc:python-reviewer` → `ecc:rag-pipeline-reviewer`
- After 1b: `/frontier-digest-review`
- Before 1c: `/frontier-plan` + Preference Gate 1c
- Implement 1c: ECC `/feature-dev` → `ecc:react-reviewer`
- After 1c: `/frontier-ui-check`
- After all: `/frontier-phase-gate`

**Definition of Done:**
- [ ] At least 2 sources fetching and storing correctly
- [ ] Every digest item has: narrative summary, source name, direct link to original
- [ ] Digest shows max 5–10 items per domain
- [ ] UI renders correctly at 375px (no horizontal scroll)
- [ ] Domain filter chips work — clicking a chip filters the displayed items
- [ ] Source links open the correct original content
- [ ] `/code-review` passed for all new code

---

### Phase 2 — Expanding Sources & Automation

**Sub-phases:**
- `2a` Add remaining data sources one at a time using `/frontier-source-add`
- `2b` Automated refresh scheduler (every 48 hours)
- `2c` Thumbs-up / thumbs-down feedback system
- `2d` UI polish based on real usage feedback
- `2e` Push / email notification when digest refreshes

**Preference Gate 2 — Ask before 2a:**
```
1. Which sources do you want to add next? Review ideas_v2.md source list.
2. Are you satisfied with the narrative digest quality from Phase 1?
   Any changes to the prompt or style?
3. Should the scheduler run at a fixed time each day (e.g., 6:00 AM)
   or elapsed time (48h from last successful run)?
4. Feedback system: thumbs up/down per item, or per-domain rating?
5. Any UI pain points from using the Phase 1 build?
```

**ECC Skills:**
- Each new source: `/frontier-source-add`
- After each source: `ecc:python-reviewer` + `ecc:database-reviewer`
- After scheduler: `ecc:python-reviewer` + `ecc:silent-failure-hunter`
- After feedback system: `ecc:python-reviewer` + `ecc:react-reviewer`
- End of phase: `/frontier-phase-gate`

**Definition of Done:**
- [ ] All planned sources fetching correctly
- [ ] Scheduler running and logging correctly
- [ ] Feedback system stores thumbs-up/down with item reference
- [ ] No silent failures — errors are logged and surfaced
- [ ] `/security-scan` passed

---

### Phase 3 — Personalization

**Sub-phases:**
- `3a` Preference engine — learns from feedback history
- `3b` Topic-based filtering (user-configurable interest weights)
- `3c` Content reranking based on preferences

**Preference Gate 3 — Ask before 3a:**
```
1. After using Phase 2, which domains are you clicking on most?
   This informs the initial preference weight calibration.
2. Should preference learning be automatic (silent) or show you why
   something was surfaced ("shown because you liked similar content")?
3. How aggressive should reranking be? Light nudge or strong filter?
```

**ECC Skills:**
- Before: `/frontier-plan` → ECC `ecc:planner`
- After preference engine: `ecc:mle-reviewer` + `ecc:rag-pipeline-reviewer`
- End of phase: `/frontier-phase-gate`

---

### Phase 4 — Multi-User

**Sub-phases:**
- `4a` User authentication (NextAuth.js)
- `4b` Per-user preference storage
- `4c` Per-user personalized content feed

**Preference Gate 4 — Ask before 4a:**
```
1. What auth providers do you want? (Google recommended as primary)
2. Should new users start with your current preferences as defaults,
   or start with no preferences and build from scratch?
3. Should there be an invite-only system or open registration?
4. Any compliance or data privacy requirements to be aware of?
```

**ECC Skills:**
- Before: `/frontier-plan` + `/frontier-prd` for Phase 4
- Auth implementation: `ecc:python-reviewer` + `ecc:react-reviewer` + `ecc:security-reviewer`
- Before deploy: `/frontier-deploy` + `/security-scan`

---

## Code Standards

### Python (Backend)
- Python 3.12; use `uv` for dependency management
- Type hints on all function signatures — no `Any` unless unavoidable
- FastAPI: use `Depends()` for dependency injection, never globals
- Async: use `async def` for all route handlers and I/O-bound operations
- Pydantic v2 models for all request/response schemas
- SQLAlchemy 2.0 (async) for all database access
- All fetcher functions must return a typed dataclass, never raw dicts
- Every fetcher must handle: rate limits, timeouts, empty responses, and source downtime without crashing the pipeline
- Logging: use Python `logging` (not `print`); structured JSON logs in production

### Next.js / TypeScript (Frontend)
- TypeScript strict mode — no implicit `any`
- App Router only — no Pages Router
- Server Components by default; Client Components only when interactivity is needed
- Tailwind CSS only — no inline styles, no CSS modules
- All API calls through `lib/api.ts` — never call the backend directly from components
- Mobile-first CSS: write base styles for mobile, use `md:` and `lg:` breakpoints for larger screens
- Every interactive element must have a visible focus state

### Database
- All schema changes via Alembic migrations — never modify tables manually
- No raw SQL strings — use SQLAlchemy ORM or Core
- All migrations must be reversible (include `downgrade()`)

### General
- No secrets in code — all secrets in environment variables, documented in `.env.example`
- No `TODO` comments in committed code — open a GitHub issue instead
- Tests required for all fetchers and all API endpoints before a sub-phase is done

---

## Source Management

When adding or modifying data sources:
1. Always run `/frontier-source-add` first
2. Each source lives in its own file: `backend/app/services/fetchers/<source_name>.py`
3. All fetchers implement the same interface (defined in `fetchers/base.py`)
4. Each fetcher must: store the source URL, timestamp, domain tag, and a direct link to the original item
5. Rate limits must be respected — add `asyncio.sleep()` where needed
6. If a source goes down, the pipeline continues — failure of one source must not block others

---

## Digest Quality Rules

Every generated digest must meet these standards:
- Each item: 2–4 sentences, narrative style, no bullet points within the item
- Tone: like a knowledgeable colleague briefing you, not a press release
- Each item ends with: `Source: [Publication Name](direct_url_to_original)`
- Max 5–10 items per domain per digest — if more are found, rank and cut
- No duplicate topics across items in the same digest cycle
- No items older than the refresh window (48 hours)

---

## Environment Variables

Document all in `.env.example`. Required variables (to be finalized in Phase 0d):

```
# Backend
DATABASE_URL=postgresql+asyncpg://...
ANTHROPIC_API_KEY=
YOUTUBE_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Scheduler
REFRESH_INTERVAL_HOURS=48
MAX_ITEMS_PER_DOMAIN=10
```

---

## Important Reminders for Every Session

1. Read `ideas_v2.md` if making any product decisions
2. Check the **Active Status** table at the top of this file — update it before ending the session
3. If you are about to write code and no plan document exists in `docs/plans/` for this sub-phase, stop and run `/frontier-plan` first
4. After any code change, run `/code-review` (ECC) before calling the work done
5. After any UI change, run `/frontier-ui-check` before calling the work done
6. Ask the user before making any technology, architecture, or design decisions not already documented here
