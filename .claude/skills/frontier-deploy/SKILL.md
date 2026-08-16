# /frontier-deploy

**When to invoke:** Before any production deployment — first deploy or any subsequent update to production.

---

## What This Skill Does

Runs a comprehensive pre-deployment checklist to ensure Frontier Brief is safe, stable, and correctly configured before it goes live.

---

## Steps

### 1. Confirm Deployment Intent
Ask the user:
```
1. Which environment are we deploying to? (staging / production)
2. What changed since the last deployment?
3. Have all quality gates been passed for this phase?
   (/frontier-phase-gate must have run and passed)
```

Do not proceed if `/frontier-phase-gate` has not been run and passed for the current phase.

### 2. Security Scan
Run ECC `ecc:security-reviewer` or `/security-scan` on all changed files.

Check specifically:
- [ ] No API keys, secrets, or credentials in any committed file
- [ ] `.env` is in `.gitignore` — confirm with `git check-ignore .env`
- [ ] `.env.example` exists and documents every required variable (with no real values)
- [ ] No hardcoded URLs pointing to `localhost` in production code
- [ ] The `ANTHROPIC_API_KEY` and other API keys are loaded from environment variables only
- [ ] FastAPI CORS settings are restrictive in production (not `allow_origins=["*"]`)
- [ ] No debug mode or verbose logging left active in production config

### 3. Database Migration Check
- [ ] All Alembic migrations have been generated for schema changes in this phase
- [ ] Migrations are reversible (both `upgrade()` and `downgrade()` implemented)
- [ ] Migration has been tested against a copy of the production database schema (not just dev)
- [ ] The migration order is correct — no dependencies on tables that don't exist yet

### 4. Environment Variables
- [ ] All variables in `.env.example` have real values set in the production environment (Vercel / Railway / Fly.io dashboard)
- [ ] `DATABASE_URL` points to the production database, not dev
- [ ] `NEXT_PUBLIC_API_URL` points to the production backend URL
- [ ] `ANTHROPIC_API_KEY` is set and has sufficient credits for the expected request volume

### 5. Build Verification
- [ ] `pip install -r requirements.txt` succeeds cleanly (no version conflicts)
- [ ] FastAPI app starts without errors: `uvicorn app.main:app`
- [ ] Next.js builds without errors: `npm run build`
- [ ] No TypeScript errors in the frontend build output

### 6. Final UI Check
Run `/frontier-ui-check` one final time against the production build (or staging if available).

### 7. Rollback Plan
Before deploying, confirm:
```
If this deployment causes an issue, what is the rollback plan?
- Can we redeploy the previous version immediately? (Yes/No)
- Are there any database migrations that are irreversible?
- Is there any data that could be lost if we roll back?
```

Document the rollback plan in `docs/architecture/deploy-log.md`.

### 8. Deploy
Only after all checks pass, proceed with deployment:
- Backend: push to Railway / Fly.io
- Frontend: push to Vercel (or `vercel --prod`)
- Run database migrations against production

### 9. Post-Deploy Verification
After deployment:
- [ ] Open the production URL on a real mobile phone
- [ ] Verify the digest loads and displays correctly
- [ ] Verify at least one source link opens the correct original content
- [ ] Verify filter chips work
- [ ] Check the FastAPI health endpoint: `GET /health`
- [ ] Check application logs for errors in the first 5 minutes after deploy

Report the result to the user.

---

## Related ECC Skills
- `ecc:security-reviewer` — Security audit before deploy
- `/frontier-phase-gate` — Must pass before this skill runs
- `/frontier-ui-check` — Final UI verification
- `ecc:performance-optimizer` — If load time is a concern pre-launch
