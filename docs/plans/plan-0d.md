# Plan: Phase 0d — Project Scaffold

## Goal
Create the complete monorepo directory structure, stub all placeholder files, write all deployment configs, push to GitHub (`frontier-brief`), and walk through the one-time service setup for Vercel, Railway, and Neon — leaving the codebase in a state where a single `git push` triggers auto-deploys to all three services.

---

## Accounts to Set Up (user does this in the browser before implementation starts)

| Service | URL | How | Cost |
|---------|-----|-----|------|
| Vercel | vercel.com | Sign up with GitHub | Free |
| Railway | railway.app | Sign up with GitHub | Free ($5 credit) |
| Neon | neon.tech | Sign up with GitHub or email | Free (0.5GB) |

---

## Files to Create

### Backend
| File | Purpose |
|------|---------|
| `backend/app/__init__.py` | Package marker |
| `backend/app/main.py` | Minimal FastAPI app with `/health` and stub `/api/digest/latest` |
| `backend/app/api/__init__.py` | Package marker |
| `backend/app/core/__init__.py` | Package marker |
| `backend/app/core/config.py` | Pydantic Settings — loads all env vars, typed |
| `backend/app/db/__init__.py` | Package marker |
| `backend/app/services/__init__.py` | Package marker |
| `backend/app/services/fetchers/__init__.py` | Package marker |
| `backend/app/services/synthesis/__init__.py` | Package marker |
| `backend/app/services/scheduler/__init__.py` | Package marker |
| `backend/tests/__init__.py` | Package marker |
| `backend/tests/fetchers/__init__.py` | Package marker |
| `backend/tests/synthesis/__init__.py` | Package marker |
| `backend/tests/api/__init__.py` | Package marker |
| `backend/requirements.txt` | All Python dependencies pinned |
| `backend/alembic.ini` | Alembic config pointing to `app/db/migrations/` |
| `backend/Dockerfile` | Railway build — Python 3.12 slim, installs deps, runs uvicorn |

### Frontend
| File | Purpose |
|------|---------|
| `frontend/package.json` | Next.js 14 + React 18 + Tailwind |
| `frontend/tsconfig.json` | TypeScript strict mode |
| `frontend/next.config.ts` | Next.js config (output: standalone for Railway if needed) |
| `frontend/tailwind.config.ts` | Tailwind — mobile-first, no extra plugins yet |
| `frontend/postcss.config.mjs` | PostCSS for Tailwind |
| `frontend/src/app/layout.tsx` | Root layout — sets `<html lang>`, applies Tailwind base |
| `frontend/src/app/page.tsx` | Placeholder home — "Frontier Brief is coming soon" |
| `frontend/src/app/globals.css` | Tailwind directives (`@tailwind base/components/utilities`) |
| `frontend/src/lib/api.ts` | Stub API client — `getLatestDigest()` placeholder |
| `frontend/src/lib/types.ts` | Stub TypeScript types — `DigestItem`, `DigestCycle` |

### Root config
| File | Purpose |
|------|---------|
| `.env.example` | Every environment variable documented with instructions |
| `.gitignore` | Node, Python, env files, build outputs |
| `railway.toml` | Railway build config — points to `backend/Dockerfile` |
| `vercel.json` | Vercel config — sets `rootDirectory: frontend` for monorepo |

---

## Files to Modify

| File | Change |
|------|--------|
| `CLAUDE.md` | Update Active Status to Phase 0d; mark 0d complete at end |

---

## Dependencies

| Dependency | Status |
|-----------|--------|
| GitHub account | Ready |
| Vercel account | Need to create (step 1 of implementation) |
| Railway account | Need to create (step 1 of implementation) |
| Neon account | Need to create (step 1 of implementation) |
| `git` CLI | Available (confirmed from environment) |
| No local Python/Node required | All builds happen in Vercel/Railway cloud |

---

## Implementation Order

### Stage A — Service accounts (user does in browser, ~10 min)
1. Create Vercel account at vercel.com — sign up with GitHub
2. Create Railway account at railway.app — sign up with GitHub
3. Create Neon account at neon.tech — sign up with GitHub or email

### Stage B — Git initialization (I run commands)
4. `git init` in the current directory (`AI_News_Aggregator/`)
5. Create `.gitignore` first (so no secrets accidentally staged)
6. Stage docs and planning files that already exist

### Stage C — Scaffold files (I create all files)
7. Create all `backend/` files (main.py, config.py, requirements.txt, Dockerfile, alembic.ini, all `__init__.py`)
8. Create all `frontend/` files (package.json, tsconfig.json, layout.tsx, page.tsx, globals.css, api.ts, types.ts, tailwind/postcss configs)
9. Create `.env.example` with all variables documented
10. Create `railway.toml` and `vercel.json`

### Stage D — GitHub push
11. Create GitHub repo `frontier-brief` (user does via GitHub web UI or `gh` CLI — I provide the commands)
12. `git remote add origin https://github.com/<user>/frontier-brief.git`
13. `git add` + `git commit` + `git push -u origin main`

### Stage E — Service connections (user does in dashboards, ~15 min)
14. **Vercel**: Import project from GitHub → select `frontier-brief` repo → Vercel auto-detects `vercel.json` → sets root dir to `frontend/` → add env vars → deploy
15. **Railway**: New project → Deploy from GitHub → select `frontier-brief` repo → Railway reads `railway.toml` → add env vars → deploy
16. **Neon**: Create new project `frontier-brief` → create database `frontier_brief` → copy connection string for `DATABASE_URL`

### Stage F — Verify
17. Verify Vercel deployment: open `frontier-brief.vercel.app` → see placeholder page
18. Verify Railway deployment: open Railway URL + `/health` → `{"status": "ok"}`
19. Update `CLAUDE.md` Active Status to Phase 1 ready

---

## Environment Variables Summary

All documented in `.env.example`. Values to fill before Phase 1a:

| Variable | Where set | Source |
|----------|-----------|--------|
| `DATABASE_URL` | Railway | Neon dashboard → connection string |
| `ANTHROPIC_API_KEY` | Railway | Anthropic Console |
| `YOUTUBE_API_KEY` | Railway | Google Cloud Console |
| `REFRESH_KEY` | Railway + Vercel | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `NEXT_PUBLIC_API_URL` | Vercel | Railway dashboard → public URL of backend service |
| `NEXT_PUBLIC_REFRESH_KEY` | Vercel | Same value as `REFRESH_KEY` |

---

## Risks & Open Questions

| Risk | Mitigation |
|------|-----------|
| Railway free $5 credit — may need credit card | Railway requires a card to activate free tier; no charge until credit exhausted |
| Neon connection string format | `postgresql+asyncpg://` prefix required for SQLAlchemy async — documented in `.env.example` |
| Vercel monorepo detection | `vercel.json` with `rootDirectory: "frontend"` handles this explicitly |
| `NEXT_PUBLIC_REFRESH_KEY` visible in browser JS | Acceptable — key only triggers a digest refresh of public AI news; Anthropic spend cap is the backstop |
| YouTube API key | Created in Google Cloud Console (free, 10k units/day) — needed before Phase 1a |

---

## Acceptance Criteria

- [ ] All directories and stub files created per the structure above
- [ ] `.env.example` documents every variable with instructions
- [ ] `backend/Dockerfile` builds cleanly on Railway
- [ ] `frontend/` passes Vercel Next.js build
- [ ] GitHub repo `frontier-brief` created and all files pushed
- [ ] Vercel auto-deploys → `frontier-brief.vercel.app` responds with placeholder page
- [ ] Railway auto-deploys → backend health endpoint returns `{"status": "ok"}`
- [ ] Neon database provisioned and `DATABASE_URL` ready for Phase 1a
- [ ] `CLAUDE.md` Active Status updated to Phase 1

---

## ECC Skills to Run

| When | Skill |
|------|-------|
| After scaffold files are written | `ecc:code-reviewer` — review main.py, config.py, Dockerfile |
| After Vercel + Railway deploy successfully | Manually verify both endpoints |
| After this phase is fully done | `/frontier-phase-gate` (optional, since this is a scaffold not feature work) |
