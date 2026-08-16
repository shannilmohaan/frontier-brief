# AI News Aggregator — Project Vision

## Problem

The AI field is moving faster than any individual can track. New GitHub repositories, research papers, large language models, products, and model launches appear every alternate week. Missing even two weeks means falling significantly behind. The signal is scattered across X.com, LinkedIn, Reddit, research conferences, newsletters, and expert commentary — impossible for one person to monitor manually.

The core challenge is not access — the user is already on X.com, LinkedIn, and Reddit. The challenge is **noise**: there is too much content and no reliable way to know which posts, threads, or announcements actually matter. This project solves the noise problem by aggregating signal from high-quality, curated sources and surfacing only what is most relevant.

## Vision

A personal website that continuously monitors activity across the AI ecosystem, aggregates the most relevant developments from the past two days, and synthesizes them into short narrative digests — filtered by specific areas of interest. Every item links directly back to its original source so the user can click through and read the full post, paper, or thread instantly.

---

## Website Name

**Frontier Brief** — "Frontier" is the exact word the AI community uses for cutting-edge models and research. "Brief" signals the digest format. Clean, professional, and specific.

---

## Topics of Interest

The aggregator will prioritize content related to the following domains:

1. **Agentic AI** — agent frameworks, multi-agent systems, orchestration (LangChain, LlamaIndex, CrewAI, AutoGen, and newer entrants)
2. **New Model Capabilities** — frontier model releases, benchmarks, reasoning improvements, multimodality
3. **Context Management** — long-context techniques, memory systems, retrieval-augmented generation (RAG), in-context learning
4. **Token Economics** — cost of inference, context window pricing, efficiency improvements, quantization
5. **Tool Use & Function Calling** — how models interact with external systems, APIs, and environments
6. **AI Coding Agents** — Cursor, Devin, Claude Code, GitHub Copilot Workspace, and the broader coding agent space
7. **Reasoning & Planning** — chain-of-thought, o1/o3-style reasoning, planning under uncertainty
8. **Agent Memory & Persistence** — short-term vs. long-term memory, episodic memory, knowledge graphs for agents
9. **Applied AI Engineering** — production patterns, latency optimization, evals, observability for LLM apps
10. **AI Research** — landmark papers in the above areas from top institutions and labs

---

## Source Quality & Citation Principles

The quality of the digest is entirely determined by the quality of the sources it draws from. These principles are non-negotiable:

1. **Every item must cite its source** — no summary is shown without a link to the original. No exceptions.
2. **Direct clickable links** — each digest item links directly to the original content: the specific tweet, Reddit thread, paper PDF, GitHub repo, or blog post. One tap opens the source.
3. **Curated source list** — the aggregator pulls only from the specific people, accounts, and publications listed below. A broad crawl without curation produces noise, not signal.
4. **Source authority weighting** — content from top researchers and primary sources is ranked higher than community commentary.

---

## Data Sources — Recommended List

### YouTube (Priority: Highest)

> Video is a primary consumption format. YouTube is listed first.

| Channel | URL | Why It Matters |
|---------|-----|----------------|
| Andrej Karpathy | https://www.youtube.com/@AndrejKarpathy | From-scratch ML; deep technical commentary on model internals |
| Yannic Kilcher | https://www.youtube.com/@YannicKilcher | Deep paper walkthroughs; one of the best for understanding research |
| Two Minute Papers | https://www.youtube.com/@TwoMinutePapers | Accessible paper summaries; good for breadth |
| AI Explained | https://www.youtube.com/@aiexplained-official | Frontier model analysis; practical implications |
| Matthew Berman | https://www.youtube.com/@matthew_berman | New model releases and tooling; fast turnaround |
| David Shapiro | https://www.youtube.com/@DavidShapiroAutomator | Agentic AI; autonomous systems |
| Sam Witteveen | https://www.youtube.com/@samwitteveenai | LangChain, agents, practical LLM engineering |
| All-In Podcast (AI segments) | https://www.youtube.com/@allinpodcast | Business and strategic implications of AI |

### Research Papers

| Source | URL | Why It Matters |
|--------|-----|----------------|
| arXiv (cs.AI, cs.LG, cs.CL) | https://arxiv.org/list/cs.AI/recent | Primary preprint server for all AI/ML research |
| Papers With Code | https://paperswithcode.com | Links papers to their GitHub implementations; tracks SOTA benchmarks |
| Hugging Face Papers | https://huggingface.co/papers | Community-curated daily paper highlights with discussion |
| Semantic Scholar | https://www.semanticscholar.org | AI-powered paper discovery with citation graphs |

### Company Blogs & Official Announcements

| Source | URL | Why It Matters |
|--------|-----|----------------|
| OpenAI Blog | https://openai.com/blog | GPT, DALL-E, Sora, and policy announcements |
| Anthropic Blog | https://www.anthropic.com/news | Claude model releases, safety research |
| Google DeepMind Blog | https://deepmind.google/discover/blog/ | Gemini, AlphaFold, fundamental research |
| Google AI Blog | https://blog.google/technology/ai/ | Broader Google AI product and research news |
| Meta AI Blog | https://ai.meta.com/blog/ | LLaMA, PyTorch, open-source AI |
| Microsoft AI Blog | https://blogs.microsoft.com/ai/ | Copilot, Azure AI, OpenAI partnership news |
| Mistral AI Blog | https://mistral.ai/news/ | Efficient open-weight model releases |
| xAI Blog | https://x.ai/news | Grok model releases |
| Cohere Blog | https://cohere.com/blog | Enterprise LLM and RAG developments |

### GitHub

| Source | URL | Why It Matters |
|--------|-----|----------------|
| GitHub Trending (Python / ML) | https://github.com/trending/python?since=weekly | Surface new open-source AI tools and repos each week |
| Hugging Face Hub | https://huggingface.co/models | New model releases, datasets, and spaces |

### Reddit — Subreddits

| Subreddit | URL | Why It Matters |
|-----------|-----|----------------|
| r/MachineLearning | https://www.reddit.com/r/MachineLearning/ | Serious ML research discussion; paper authors post here |
| r/LocalLLaMA | https://www.reddit.com/r/LocalLLaMA/ | Local model releases, quantization, practical deployment |
| r/artificial | https://www.reddit.com/r/artificial/ | General AI news and discussion |
| r/singularity | https://www.reddit.com/r/singularity/ | AGI, frontier model news, futurist perspective |
| r/OpenAI | https://www.reddit.com/r/OpenAI/ | OpenAI product updates and community reaction |

### X.com — Key Accounts to Follow

| Account | Handle | Why It Matters |
|---------|--------|----------------|
| Sam Altman | @sama | CEO of OpenAI; announces major releases |
| Andrej Karpathy | @karpathy | Former OpenAI/Tesla; deep technical breakdowns |
| Yann LeCun | @ylecun | Chief AI Scientist at Meta; rigorous and contrarian |
| Demis Hassabis | @demishassabis | CEO of Google DeepMind |
| Jim Fan | @DrJimFan | NVIDIA AI research; robotics and embodied AI |
| François Chollet | @fchollet | Keras creator; ARC benchmark; reasoning research |
| Ethan Mollick | @emollick | Wharton professor; practical AI impact research |
| Jeremy Howard | @jeremyphoward | fast.ai; practical deep learning |
| Harrison Chase | @hwchase17 | Creator of LangChain; agentic AI tooling |
| Gary Marcus | @GaryMarcus | Critical AI perspective; useful counterbalance |
| Anthropic | @AnthropicAI | Official Anthropic announcements |
| Hugging Face | @huggingface | Open-source ML releases and community news |

### LinkedIn — Key People & Pages

| Who | Why It Matters |
|-----|----------------|
| Andrew Ng | AI educator; founder of deeplearning.ai; weekly newsletter |
| Yann LeCun | Meta Chief AI Scientist |
| Fei-Fei Li | Stanford AI Lab; AI policy and vision research |
| Sam Altman | OpenAI |
| OpenAI (company page) | Official product and research announcements |
| Anthropic (company page) | Claude and safety research |
| Google DeepMind (company page) | Research and product announcements |

### Newsletters & Substacks

| Newsletter | URL | Why It Matters |
|-----------|-----|----------------|
| The Batch (deeplearning.ai) | https://www.deeplearning.ai/the-batch/ | Weekly digest by Andrew Ng; high signal-to-noise |
| Import AI | https://importai.substack.com | Weekly by Jack Clark (Anthropic co-founder); research focus |
| Ahead of AI | https://magazine.sebastianraschka.com | Deep technical breakdowns; model internals |
| Interconnects | https://www.interconnects.ai | Nathan Lambert (Allen AI); RLHF and model training |
| One Useful Thing | https://www.oneusefulthing.org | Ethan Mollick; practical AI use and research |
| The Gradient | https://thegradient.pub | Long-form AI research commentary |
| Last Week in AI | https://lastweekin.ai | Weekly roundup; broad coverage |
| Ben's Bites | https://www.bensbites.co | Daily AI product and research news |
| TLDR AI | https://tldr.tech/ai | Daily digest; concise format |
| The Algorithmic Bridge | https://thealgorithmicbridge.substack.com | Alberto Romero; thoughtful AI commentary |

### Conferences

| Conference | URL | Focus |
|-----------|-----|-------|
| NeurIPS | https://neurips.cc | Flagship ML/AI research conference |
| ICML | https://icml.cc | Machine learning theory and applications |
| ICLR | https://iclr.cc | Deep learning and representation learning |
| ACL / EMNLP / NAACL | https://aclanthology.org | Natural language processing |
| CVPR | https://cvpr.thecvf.com | Computer vision |
| AI Engineer Summit | https://www.ai.engineer | Applied AI engineering; LLMs in production |

### Aggregator & Discovery Sites

| Source | URL | Why It Matters |
|--------|-----|----------------|
| Hacker News | https://news.ycombinator.com | High-quality technical discussion on AI tools and research |
| AlphaSignal | https://alphasignal.ai | Useful reference and benchmark for this project |
| Stanford HAI AI Index | https://aiindex.stanford.edu | Annual comprehensive state-of-AI report |
| Product Hunt (AI category) | https://www.producthunt.com/topics/artificial-intelligence | New AI product launches daily |

---

## Key Features

### 1. Multi-Source Aggregation
- Monitor all configured sources simultaneously
- Pull updates every two days (background job)
- Deduplicate and rank content by relevance and recency
- **Volume cap: quality over quantity** — the digest shows a small, curated set of items per refresh (target: 5–10 items per domain, not hundreds). The whole point is to replace the noise of an open feed, not recreate it. The AI does the filtering so the user does not have to.

### 2. Synthesis & Digest — Short Narrative Format
- Summarize top developments in short narrative paragraphs (not bullet lists)
- Conversational, easy-to-read tone — like a smart colleague briefing you on what you missed
- Every digest item includes: a 2–4 sentence narrative summary, the source name, and a direct clickable link to the original

### 3. Direct Links to Original Content
- Each item links to the exact source: the specific video, tweet, Reddit thread, paper PDF, GitHub repo, or blog post
- One tap on mobile opens the original content directly
- The digest is a curated entry point — the user always has an escape hatch to the real source

### 4. Domain Grouping & Filtering
- All digest items are tagged with one or more of the defined topics of interest (e.g., "Agentic AI", "Context Management", "New Models")
- The UI groups items by domain — each topic gets its own section or tab in the digest
- The user can filter to a single domain at any time and see only items from that area
- On mobile, this is a horizontal filter chip bar at the top — one tap switches the active domain
- Default view shows all domains in order of most activity in the current digest cycle

### 6. Personalization & Feedback
- Content filtered by the defined topics of interest
- Thumbs-up / thumbs-down feedback system per item
- System learns preferences over time and adjusts what is surfaced

### 7. Content Refresh
- Automated refresh every two days
- Runs in the background; user always sees the latest available snapshot on visit

---

## UI & Design

- **Extremely modern, clean interface** — should feel premium and intentional, not a generic news aggregator
- **Mobile-first** — primary use case is browsing on a phone while traveling; the mobile experience is the priority
- **Fully responsive** — works equally well on phone and laptop
- **Fast and lightweight** — content immediately readable; no heavy page loads
- **Skimmable layout** — digest-style cards, clear hierarchy, readable in under 60 seconds per section
- **Tap-to-source** — every card has a clearly visible button/link that opens the original source in one tap
- **Design standard** — latest UI trends: fluid layouts, clean typography, generous whitespace, subtle motion

---

## Tech Stack (Proposed)

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Python + FastAPI | Fast async API; Python ecosystem for LLM and data pipeline work |
| **Frontend** | Next.js + Tailwind CSS | Best-in-class mobile-responsive UI; fast rendering; large ecosystem |
| **Database** | PostgreSQL | Structured storage for digest items, sources, feedback |
| **Vector Store** | pgvector (or Qdrant) | Semantic similarity for deduplication and relevance ranking |
| **Task Scheduler** | APScheduler or Celery + Redis | Background refresh jobs every two days |
| **LLM (Synthesis)** | Claude API (Anthropic) | Narrative digest generation; citation-aware summarization |
| **Hosting (Dev)** | Local / Docker | Development environment |
| **Hosting (Prod)** | Vercel (frontend) + Railway or Fly.io (backend) | Simple, scalable, low-maintenance |

> Final stack decisions to be confirmed in Phase 0c.

---

## Development Philosophy

- **Plan before build** — no implementation begins without a versioned plan document
- **Project roadmap** — a formal roadmap to be created before any development starts
- **Staged delivery** — development environment first, production deployment only after validation
- **Incremental features** — start simple, validate, then layer on complexity; never build everything at once
- **Iterative improvement** — user feedback drives continuous refinement of content quality and relevance

---

## Phases & Sub-Phases

### Phase 0 — Planning & Architecture
> *No code written in this phase.*

- **0a** — Finalize requirements ✅ *(this document)*
- **0b** — Write formal PRD (Product Requirements Document)
- **0c** — Confirm system architecture and tech stack
- **0d** — Set up project scaffold and development environment

### Phase 1 — MVP (Single User, No Auth)

- **1a** — Data pipeline for 2–3 sources (YouTube + arXiv + one newsletter to start)
- **1b** — Basic synthesis engine: LLM-powered narrative digest with citations
- **1c** — Minimal web UI — mobile-first, digest cards with direct source links
- **1d** — Manual refresh trigger (no scheduler yet)

### Phase 2 — Expanding Sources & Automation

- **2a** — Add remaining data sources incrementally
- **2b** — Automated refresh scheduler (every two days)
- **2c** — Thumbs-up / thumbs-down feedback system
- **2d** — UI improvements based on real usage
- **2e** — Push / email notification when digest refreshes *(deferred from Phase 1)*

### Phase 3 — Personalization

- **3a** — Preference engine: learns from feedback history
- **3b** — Topic-based filtering (user-configurable)
- **3c** — Content reranking based on preferences

### Phase 4 — Multi-User

- **4a** — User authentication
- **4b** — Per-user preference storage
- **4c** — Per-user personalized content feed

---

## ECC Development Workflow

This project will follow the ECC (Everything Claude Code) skill-based workflow for structured, quality-gated development.

| Stage | ECC Skill / Command | Purpose |
|-------|---------------------|---------|
| Project setup | `/project-init` | Scaffold the project, configure Claude Code for the stack |
| Requirements | `/plan-prd` | Write the formal Product Requirements Document (Phase 0b) |
| Architecture | `/blueprint` | Design system architecture before any code is written |
| Feature planning | `/plan` | Sprint-level planning within each sub-phase |
| Feature build | `/feature-dev` | Implement one feature at a time, in order |
| Code review | `/code-review` | Review every change before it is considered done |
| Security | `/security-scan` | Run before any production deployment |
| Refactoring | `/refactor-clean` | Clean up after feature completion, not during |

**Rule:** No sub-phase begins without a plan. No code ships without a review.

---

## Resolved Decisions

| Question | Decision |
|----------|----------|
| Website name | **Frontier Brief** |
| Topics of interest | Agentic AI, model capabilities, context management, token economics, tool use, coding agents, reasoning, agent memory, applied AI engineering |
| Refresh cadence | Every two days |
| Synthesis format | Short narrative digest (conversational paragraphs, not bullet lists) |
| Volume per refresh | 5–10 curated items per domain — no firehose |
| Domain filtering | Grouped by topic; filter chips on mobile; default shows all |
| Backend | Python + FastAPI |
| Frontend | Next.js + Tailwind CSS |
| YouTube | Yes — highest priority source category |
| Notifications | Deferred to Phase 2 |
| Authentication | Phase 4 |

## Open Questions

- [ ] **Topics of interest** — review the 10 listed above and confirm or adjust the list before Phase 0 completes

---

*This document is a living vision. Phase 0 begins once the website name is chosen and the topic list is confirmed.*
