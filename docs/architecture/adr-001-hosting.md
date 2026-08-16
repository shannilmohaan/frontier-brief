# ADR-001: Hosting Stack — Vercel + Railway + Neon

**Date:** 2026-08-15
**Status:** Accepted
**Deciders:** Shanir + Claude Code

## Context

Frontier Brief needs fully cloud-hosted infrastructure (nothing runs locally), accessible from any device, with a hard cost ceiling of $0–$5/month. The user must not receive surprise bills regardless of traffic.

## Decision

| Component | Choice |
|-----------|--------|
| Frontend | Vercel (free tier) |
| Backend | Railway (free $5 credit/month) |
| Database | Neon (free tier, serverless PostgreSQL) |

## Consequences

**Positive:**
- Zero local setup required — write code, push to GitHub, it's live
- All three services auto-deploy from GitHub pushes
- Hard cost ceilings: services stop at limits, they do not charge overages
- Neon's serverless PostgreSQL requires no DB server management
- Railway supports APScheduler (long-running process) — critical for the 48h refresh job

**Negative / Trade-offs:**
- Railway free credit ($5/month) may be exhausted by a particularly active month — service stops until the next billing period
- Neon free tier (0.5GB) will be sufficient for ~6–12 months of digest data; migration needed if storage grows
- No automatic failover — if Railway goes down, the digest API is unavailable

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Render (backend) | Free tier spins down after 15min inactivity; 30–60s cold start on first request |
| Fly.io (backend) | More complex config; Railway is simpler for a FastAPI + scheduler setup |
| Supabase (database) | More features than needed for Phase 1; Neon is simpler pure PostgreSQL |
| AWS / GCP / Azure | No free tier that covers all needs without risk of surprise bills |
| Full Vercel (frontend + serverless API) | Serverless functions have 10s timeout; synthesis pipeline takes 2–3 minutes |

## Phase 4 Revisit

When multi-user auth is added in Phase 4, revisit the database choice:
- **Supabase** has built-in auth, row-level security, and a generous free tier — becomes the better choice when user accounts are needed.
- Migration from Neon to Supabase is straightforward (same PostgreSQL, just a connection string change + data export/import).
