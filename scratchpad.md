# Frontier Brief — Setup & Configuration Scratchpad

> Living document for service accounts, env vars, deployment steps, and config decisions.
> Update this file whenever a service is configured or a key decision is made.

---

## Status Snapshot

| Service | Status | Notes |
|---------|--------|-------|
| GitHub | ✅ Repo created, public | `frontier-brief` |
| Railway | 🔄 Build passing, env vars pending | Root dir set to `backend/` |
| Neon | ⏳ Not yet created | Need DATABASE_URL |
| Vercel | ⏳ Not yet created | Need NEXT_PUBLIC_API_URL |

---

## 1. GitHub

**What:** Source of truth for all code. Railway and Vercel auto-deploy on every push to `main`.

**Steps completed:**
- [x] Created public repo `frontier-brief`
- [x] Pushed monorepo (both `backend/` and `frontend/` in one repo)

**Key decision:** Monorepo — single GitHub repo, Railway deploys `backend/`, Vercel deploys `frontend/`.

---

## 2. Neon (PostgreSQL database)

**What:** Serverless PostgreSQL for all three tables (`digest_cycles`, `source_items`, `digest_items`). Free tier: 0.5 GB.

**Setup steps:**
1. Go to https://neon.tech → sign in with GitHub
2. Create a new project — name it `frontier-brief`
3. Choose region closest to Railway region (US East if Railway is us-east-1)
4. Once created, go to **Connection Details**
5. Copy the connection string — **important:** use the `postgresql+asyncpg://` format, not plain `postgresql://`
   - It looks like: `postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
6. Paste this into Railway as `DATABASE_URL` (see Railway section below)

**Run migrations after Railway is live:**
```
# From your local machine, with DATABASE_URL set in your shell:
cd backend
pip install alembic asyncpg
alembic upgrade head
```
Or trigger via Railway's shell once the service is running.

---

## 3. Railway (Python/FastAPI backend)

**What:** Hosts the FastAPI server + APScheduler. Free $5 credit/month.

**Setup steps:**
1. Go to https://railway.app → sign in with GitHub
2. New Project → Deploy from GitHub repo → select `frontier-brief`
3. Railway creates a service — click into it
4. **Settings → Source → Root Directory:** set to `backend`
   *(This is the critical step — without it nixpacks can't find requirements.txt)*
5. Railway will trigger a build. First build may fail until env vars are set (next step).

**Environment Variables — add all of these in Railway → your service → Variables:**

| Variable | Value | Where to get it |
|----------|-------|-----------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db?sslmode=require` | Neon → Connection Details |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | console.anthropic.com → API Keys |
| `YOUTUBE_API_KEY` | `AIza...` | console.cloud.google.com → YouTube Data API v3 |
| `REFRESH_KEY` | Any secret string (32+ chars) | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `CORS_ORIGINS` | `https://your-project.vercel.app` | Set after Vercel is configured |
| `REFRESH_INTERVAL_HOURS` | `48` | Default |
| `MAX_ITEMS_PER_DOMAIN` | `10` | Default |

**YouTube API key setup:**
1. Go to https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable "YouTube Data API v3" from the API Library
4. Credentials → Create Credentials → API Key
5. Optionally restrict the key to YouTube Data API v3 only

**Verification:**
- After env vars are saved, Railway redeploys automatically
- Check Railway logs — should see uvicorn starting on port $PORT
- Visit `https://your-railway-url.railway.app/health` → should return `{"status":"ok"}`
- Visit `https://your-railway-url.railway.app/docs` → FastAPI auto-docs

**Known issues resolved:**
- `pip: command not found` → Fixed by setting Root Directory to `backend/` (nixpacks then finds requirements.txt directly)
- `ValidationError: 4 validation errors for Settings` → Fixed by adding all 4 required env vars

---

## 4. Vercel (Next.js frontend)

**What:** Hosts the Next.js frontend. Free tier with auto-deploy on every GitHub push.

**Setup steps:**
1. Go to https://vercel.com → sign in with GitHub
2. New Project → Import Git Repository → select `frontier-brief`
3. **Framework Preset:** Next.js (Vercel auto-detects this)
4. **Root Directory:** set to `frontend`
   *(Do NOT put `rootDirectory` in vercel.json — Vercel rejected this in a recent update. Dashboard only.)*
5. Click Deploy — first deploy will show the "Frontier Brief — coming soon" placeholder page

**Environment Variables — add in Vercel → your project → Settings → Environment Variables:**

| Variable | Value | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-service.railway.app` | From Railway → your service → Settings → Domains |
| `NEXT_PUBLIC_REFRESH_KEY` | Same value as Railway's `REFRESH_KEY` | Visible in browser JS bundle — acceptable for Phase 1 (see ADR-002) |

**Note on NEXT_PUBLIC vars:** These are embedded into the client-side JavaScript bundle and visible to anyone who opens DevTools. Acceptable for Phase 1 because the Vercel URL is not publicised. Phase 4 replaces this with NextAuth.js session tokens.

**Verification:**
- Vercel gives you a preview URL on every deploy (e.g. `frontier-brief-xyz.vercel.app`)
- Visit the URL — should see the placeholder page
- After Phase 1c is implemented, the full digest UI will appear here

---

## 5. Database Migrations

**When:** After Railway is live with a valid `DATABASE_URL`.

**Option A — From Railway's shell (recommended for production):**
1. Railway → your service → Shell (or use Railway CLI)
2. Run: `cd /app && alembic upgrade head`

**Option B — From local machine:**
1. Set `DATABASE_URL` in your local environment:
   ```
   $env:DATABASE_URL = "postgresql+asyncpg://..."   # PowerShell
   ```
2. From `backend/` directory: `alembic upgrade head`

**Migration file:** `backend/alembic/versions/001_initial_schema.py`
Creates tables: `digest_cycles`, `source_items`, `digest_items`

---

## 6. CORS Configuration

After Vercel gives you a URL:
1. Go to Railway → your service → Variables
2. Update `CORS_ORIGINS` to your Vercel URL: `https://frontier-brief-xyz.vercel.app`
3. Railway redeploys automatically

For local frontend development, also add `http://localhost:3000`:
```
CORS_ORIGINS=https://frontier-brief-xyz.vercel.app,http://localhost:3000
```

---

## 7. End-to-End Verification Checklist

Run through this after all services are connected:

- [ ] `GET https://your-railway-url/health` → `{"status":"ok"}`
- [ ] `GET https://your-railway-url/docs` → FastAPI Swagger UI loads
- [ ] `GET https://your-railway-url/api/digest/latest` → `{"items":[],"domain_filter":null,"cycle_id":null}`
- [ ] `POST https://your-railway-url/api/refresh` with header `X-Refresh-Key: your-key` → `{"job_id":"...","status":"accepted"}`
- [ ] `POST https://your-railway-url/api/refresh` with wrong key → `{"detail":"Invalid refresh key"}` (401)
- [ ] Vercel URL loads placeholder page in browser
- [ ] Database migration ran: all 3 tables exist in Neon console

---

## 8. Cost Ceiling

| Service | Plan | Monthly cost |
|---------|------|-------------|
| GitHub | Free | $0 |
| Neon | Free (0.5 GB) | $0 |
| Railway | Free ($5 credit) | $0–$5 |
| Vercel | Free (Hobby) | $0 |
| Anthropic API | Pay-per-use | ~$0.10–$0.50 with $5 hard cap |
| YouTube Data API | Free quota | $0 |
| **Total** | | **< $5/month** |

**Set Anthropic spend limit:** console.anthropic.com → Billing → Usage limits → set monthly cap to $5.

---

## 9. Phase Transition Notes

### Phase 0d → Phase 1 (current)
- Scaffold complete, Phase 1a (fetchers) code written and reviewed
- Pending: Railway env vars, Neon setup, migrations, Vercel connect

### Future: Phase 4 → Multi-user
- Switch Neon free tier → Neon paid or Supabase (per ADR-001)
- Replace NEXT_PUBLIC_REFRESH_KEY with NextAuth.js session auth (per ADR-002)
- Railway free credit → paid plan if traffic justifies it
