# ADR-002: Phase 1 Security — Open Read, Protected Refresh

**Date:** 2026-08-15
**Status:** Accepted
**Deciders:** Shanir + Claude Code

## Context

Frontier Brief Phase 1 is a single-user app serving curated public AI news. The user wants it accessible from any device without a login. The primary security concern is not data privacy (no personal data is stored) but **cost protection** — specifically, preventing unauthorized calls to the expensive `/refresh` endpoint which triggers Anthropic API calls.

## Decision

**Open read, protected write:**

- `GET /api/digest/latest` — **open, no auth**. Returns cached data from the database. Zero LLM cost per request. Acceptable for anyone to access.
- `POST /api/refresh` — **protected with a static key** sent as `X-Refresh-Key` header. Stored as an env var in Vercel (`NEXT_PUBLIC_REFRESH_KEY`) and Railway (`REFRESH_KEY`). This is the only endpoint that triggers Anthropic API usage.
- All endpoints — **rate limited at 100 req/min per IP** via `slowapi`. Stops casual abuse.
- `robots.txt: Disallow: /` — prevents search engines from indexing the site. Reduces organic discovery.

## Cost Protection Layers

1. `/refresh` key — stops unauthorized LLM triggers
2. Anthropic spend limit ($5/month cap in Anthropic Console) — hard ceiling on API costs
3. Railway free credit hard cap — backend stops, doesn't bill
4. Rate limiting — prevents API abuse even on open endpoints
5. `robots.txt` — reduces discovery

## Consequences

**Positive:**
- No login screen — app opens immediately on phone or laptop
- Simple to implement — one header check in FastAPI
- Anthropic cost is fully controlled — only runs on schedule + authorized manual refresh
- The digest content is public AI news — no privacy risk in leaving reads open

**Negative / Trade-offs:**
- Anyone who finds the URL can read the digest — acceptable by user decision
- The `NEXT_PUBLIC_REFRESH_KEY` is visible in browser JavaScript — acceptable because: (a) the app's URL isn't public, (b) the key only triggers a refresh of public AI news, (c) Anthropic spend limit is the backstop
- Not suitable once multi-user or personal data is added — see Phase 4

## Phase 4 Revisit

Replace this approach with proper authentication (NextAuth.js + Supabase Auth) when multi-user support is added. At that point, per-user sessions and row-level security replace the static key.
