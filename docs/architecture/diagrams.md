# Frontier Brief — Diagrams

Two diagrams in Mermaid format. Both can be imported into Draw.io:
**Extras → Edit Diagram → (select "Mermaid" tab at bottom) → paste → OK**

---

## 1. System Architecture

```mermaid
graph TD
    DEV["💻 Local Machine\n(write code only — nothing runs here)"]
    GH["🐙 GitHub\n(monorepo)"]
    USER["📱 User Devices\nPhone · Laptop"]

    DEV -->|git push| GH
    GH -->|"auto-deploy on push"| VERCEL
    GH -->|"auto-deploy on push"| RAILWAY
    USER -->|HTTPS| VERCEL

    subgraph VERCEL ["▲ Vercel — Next.js 14 Frontend — Free tier"]
        V_PAGE["Digest Page\npage.tsx"]
        V_CHIPS["DomainFilterChips\nhorizontal scroll · mobile-first"]
        V_CARDS["DigestCard × N\nnarrative + source link"]
        V_API["lib/api.ts\nall backend calls"]
        V_ROBOTS["robots.txt\nDisallow: /"]
    end

    VERCEL -->|"REST API calls\nJSON over HTTPS"| R_API

    subgraph RAILWAY ["🚂 Railway — FastAPI Backend — Free $5 credit/month"]
        R_API["REST API Layer\nGET /api/digest/latest — open\nPOST /api/refresh — 🔑 X-Refresh-Key\nGET /api/refresh/id — open\n100 req/min/IP rate limit"]
        R_SCHED["⏰ APScheduler\nevery 48h"]
        R_PIPE["pipeline.py\norchestrator"]

        subgraph FETCHERS ["Fetchers — each runs independently"]
            F_YT["▶ YouTube\nData API v3\n5 channels"]
            F_AX["📄 arXiv\nfree API\ncs.AI/LG/CL"]
            F_TB["📰 The Batch\nRSS feed"]
            F_HF["🤗 HF Papers\ndaily feed"]
        end

        R_RANK["Ranker + Deduplicator\ndedupe · recency 60% + topic 40%\ncap 20/domain"]
        R_SYNTH["✨ Synthesis Engine\nclaude-sonnet-5\n2–4 sentence narrative · citation\ncap 5 DigestItems/domain"]
    end

    R_SCHED -->|"fires every 48h"| R_PIPE
    R_PIPE --> F_YT & F_AX & F_TB & F_HF
    F_YT & F_AX & F_TB & F_HF -->|"raw SourceItems"| R_RANK
    R_RANK -->|"ranked items"| R_SYNTH

    F_YT -->|"fetch last 48h"| EXT_YT
    F_AX -->|"fetch last 48h"| EXT_AX
    F_TB -->|"fetch last 48h"| EXT_TB
    F_HF -->|"fetch last 48h"| EXT_HF
    R_SYNTH -->|"LLM calls\n48h cycle only"| EXT_ANTHRO

    subgraph EXTERNAL ["External APIs"]
        EXT_ANTHRO["🤖 Anthropic API\nclaude-sonnet-5\nSet $5/month spend cap"]
        EXT_YT["▶ YouTube Data API v3\n10k units/day free"]
        EXT_AX["📄 arXiv API\nfree · no key"]
        EXT_TB["📰 The Batch RSS\nfree · weekly"]
        EXT_HF["🤗 HF Papers\nfree"]
    end

    R_SYNTH -->|"SQL write"| NEON
    R_API -->|"SQL read\ncached digest"| NEON

    NEON[("🐘 Neon PostgreSQL — Free 0.5GB\ndigest_cycles · source_items · digest_items")]
```

---

## 2. Sequence Diagrams

### Flow A — Normal Page Load

```mermaid
sequenceDiagram
    actor U as 📱 User
    participant V as ▲ Vercel
    participant R as 🚂 Railway
    participant N as 🐘 Neon DB

    U->>V: open app (HTTPS)
    V->>R: GET /api/digest/latest
    R->>N: SELECT latest completed DigestItems
    N-->>R: DigestItems[]
    R-->>V: { items, domains, cycle_id }
    V-->>U: render digest cards + domain filter chips
    Note over U,V: zero LLM cost — pure DB read
```

### Flow B — Manual Refresh Trigger

```mermaid
sequenceDiagram
    actor U as 📱 User
    participant V as ▲ Vercel
    participant R as 🚂 Railway
    participant N as 🐘 Neon DB
    participant C as 🤖 Anthropic API
    participant S as 🌐 Sources

    U->>V: tap Refresh button
    V->>R: POST /api/refresh (X-Refresh-Key: ***)
    R->>R: validate key
    R->>N: INSERT digest_cycle (status=in_progress)
    N-->>R: cycle_id
    R-->>V: 202 { cycle_id, status: started }
    V->>V: show loading spinner

    par fetch all sources concurrently
        R->>S: YouTube Data API (last 48h, 5 channels)
        S-->>R: video items[]
    and
        R->>S: arXiv API (cs.AI, cs.LG, cs.CL)
        S-->>R: paper items[]
    and
        R->>S: The Batch RSS
        S-->>R: newsletter items[]
    and
        R->>S: HF Papers feed
        S-->>R: paper items[]
    end

    Note over R: one fetcher failure does not stop the others

    R->>R: Ranker: dedupe by URL · score · cap 20/domain

    loop for each ranked item (batched by domain)
        R->>C: synthesize(item) → claude-sonnet-5
        C-->>R: 2–4 sentence narrative + domain tag + citation
    end

    R->>R: discard items beyond top 5 per domain
    R->>N: INSERT digest_items (narratives + citations)
    R->>N: UPDATE digest_cycle SET status=completed

    loop poll until done (every 3s)
        V->>R: GET /api/refresh/{cycle_id}
        R-->>V: { status: in_progress | completed }
    end

    V->>R: GET /api/digest/latest
    R->>N: SELECT latest DigestItems
    N-->>R: DigestItems[]
    R-->>V: updated digest
    V-->>U: render updated digest
```

### Flow C — Scheduled Refresh (no user action)

```mermaid
sequenceDiagram
    participant SCHED as ⏰ APScheduler
    participant R as 🚂 Railway
    participant N as 🐘 Neon DB
    participant C as 🤖 Anthropic API
    participant S as 🌐 Sources

    Note over SCHED: fires every 48h (also checks on startup)
    SCHED->>R: trigger pipeline()
    R->>N: SELECT MAX(completed_at) FROM digest_cycles
    N-->>R: last_completed_at
    R->>R: last_completed_at > 48h ago?

    alt yes — refresh needed
        Note over R,S: same fetch → rank → synthesize → save flow as Flow B
        R->>S: fetch all sources (parallel)
        S-->>R: raw items
        R->>R: rank + dedupe
        R->>C: synthesize (batched)
        C-->>R: narratives + citations
        R->>N: INSERT digest_items
        R->>N: UPDATE digest_cycle SET status=completed
    else no — fresh enough, skip
        R->>R: log "digest is current, skipping"
    end
```

---

## How to Import into Draw.io

1. Open [app.diagrams.net](https://app.diagrams.net) (or open Draw.io desktop app)
2. Click **Extras → Edit Diagram**
3. At the bottom of the dialog, click **Close** on the current XML view
4. Or: click the **Mermaid** tab at the bottom of the Edit Diagram dialog
5. Paste the Mermaid code block (without the ` ```mermaid ` fences) 
6. Click **OK**

The `.drawio` file in this folder (`architecture-diagram.drawio`) can be opened directly in Draw.io without any import steps.
