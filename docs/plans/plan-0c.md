# Plan: Phase 0c — Architecture Design

## Goal
Produce a complete system architecture document that defines how every component of Frontier Brief is structured, connected, and deployed — before any code is written.

## Files to Create
- `docs/architecture/architecture.md` — full system architecture: components, data flow, deployment pipeline, security, environment variables
- `docs/architecture/adr-001-hosting.md` — Architecture Decision Record for hosting choices (Railway + Vercel + Neon)
- `docs/architecture/adr-002-security.md` — ADR for Phase 1 security approach (open read + protected refresh)

## Files to Modify
- `CLAUDE.md` — update Active Status to 0d once 0c is complete; add confirmed security decisions to Non-Negotiables

## Dependencies
- All decisions from Phase 0a (ideas_v2.md) and 0b (PRD) are inputs — no external dependencies to set up yet

## Implementation Order
1. Write `docs/architecture/architecture.md` (system overview, components, data flow, deployment, security, env vars, monorepo structure)
2. Write `docs/architecture/adr-001-hosting.md`
3. Write `docs/architecture/adr-002-security.md`
4. Update `CLAUDE.md` active status

## Risks & Open Questions
- The Batch and Hugging Face Papers feed URLs need to be confirmed before 1a — noted in architecture as pending verification
- YouTube Data API quota needs estimating before fetcher is built

## Acceptance Criteria
- [ ] Architecture document covers: system components, data flow, deployment pipeline, env vars, monorepo layout, security approach
- [ ] ADRs written for the two biggest decisions (hosting, security)
- [ ] No ambiguity about how Vercel frontend talks to Railway backend
- [ ] No ambiguity about how Railway backend talks to Neon DB
- [ ] Cost ceiling strategy documented
- [ ] User has reviewed and approved

## ECC Skills to Run
- `ecc:architect` — independent review of the architecture after document is written
- `ecc:security-reviewer` — validate the security approach (open read + protected refresh + rate limiting)
