from datetime import datetime, timezone

from app.services.fetchers.base import FetchedItem

# Content taxonomy aligned to frontier-ai-specs.md §9
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Agentic AI": [
        "agent", "agentic", "autonomous agent", "multi-agent", "mcp",
        "model context protocol", "tool calling", "tool use", "function calling",
        "memory", "context engineering", "orchestration", "agent framework",
        "agent skills", "agent workflow", "self-improving", "agent orchestration",
        "hub-and-spoke", "multi-agent system",
    ],
    "AI Architecture": [
        "rag", "retrieval augmented", "agentic rag", "workflow pattern",
        "event-driven", "human-in-the-loop", "integration pattern",
        "application architecture", "vector database", "embedding", "chunking",
        "pgvector", "pinecone", "weaviate", "qdrant", "chroma",
    ],
    "AI Engineering": [
        "sdk", "langchain", "llamaindex", "llm api", "prompting",
        "evaluation", "evals", "observability", "guardrails", "ai security",
        "tracing", "weave", "braintrust", "context window",
        "prompt engineering", "structured output", "openai sdk", "anthropic sdk",
    ],
    "AI Coding": [
        "codex", "claude code", "cursor", "github copilot", "coding agent",
        "agentic software", "agentic development", "swe-bench", "devin",
        "ai coder", "automated coding", "ai programming", "ai developer",
        "vibe coding", "windsurf", "ai coding", "code generation",
    ],
    "Production AI": [
        "deployment", "scalability", "reliability", "cost optimization",
        "inference cost", "latency", "governance", "monitoring", "enterprise",
        "production", "mlops", "vllm", "ollama", "triton", "batch inference",
        "throughput", "compliance", "edge deployment", "serving",
    ],
    "Models": [
        "gpt-4", "gpt-5", "claude 3", "claude 4", "claude 5", "gemini",
        "llama", "mistral", "phi-", "qwen", "model release", "new model",
        "multimodal", "vision model", "reasoning model", "o1", "o3",
        "thinking model", "context window", "foundation model",
    ],
    "AI Applications": [
        "llm application", "enterprise ai", "ai assistant", "ai search",
        "ai automation", "chatbot", "virtual assistant", "ai product", "copilot",
    ],
    "Industry": [
        "funding", "acquisition", "partnership", "open source release",
        "policy", "regulation", "ai safety", "responsible ai",
        "research breakthrough", "series a", "series b", "ipo",
    ],
}


def classify_domains(text: str) -> list[str]:
    """Keyword-based domain classification. Returns [] if no match."""
    text_lower = text.lower()
    return [
        domain
        for domain, keywords in DOMAIN_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]


# Source credibility — keys match source_name values emitted by fetchers exactly.
_SOURCE_CREDIBILITY: dict[str, float] = {
    # Tier 1 — official AI lab sources
    "OpenAI": 1.0,
    "Anthropic": 1.0,
    "Google DeepMind": 1.0,
    "Meta AI": 1.0,
    "Microsoft AI Blog": 1.0,
    "Mistral AI Blog": 1.0,
    # Tier 1 curators / researchers
    "Andrej Karpathy": 0.95,
    "Hugging Face Blog": 0.90,
    "DeepLearning.AI Blog": 0.90,
    # Tier 2 — expert curated
    "Yannic Kilcher": 0.85,
    "Import AI": 0.85,
    "Ahead of AI": 0.85,
    "Interconnects": 0.85,
    "AWS ML Blog": 0.85,
    "fast.ai": 0.85,
    "Latent Space": 0.80,
    "Practical AI": 0.80,
    "No Priors": 0.80,
    "The Cognitive Revolution": 0.80,
    "Two Minute Papers": 0.80,
    "AI Explained": 0.80,
    "LangChain Blog": 0.80,
    "Lex Fridman Podcast": 0.75,
    "Lex Fridman": 0.75,
    "TWIML AI Podcast": 0.75,
    "Last Week in AI": 0.75,
    "The Rundown AI": 0.75,
    "Gradient Dissent": 0.75,
    "Matthew Berman": 0.75,
    "Ben's Bites": 0.70,
    "David Shapiro": 0.70,
    "Sam Witteveen": 0.70,
    "All-In Podcast": 0.70,
}
_DEFAULT_CREDIBILITY = 0.5

# 9-dimension scoring weights — per spec §13
_W_APP_RELEVANCE = 0.20
_W_PROD_USEFULNESS = 0.20
_W_LEARNING_VALUE = 0.15
_W_ARCH_IMPACT = 0.15
_W_PRACTICALITY = 0.10
_W_CREDIBILITY = 0.10
_W_NOVELTY = 0.05
_W_RECENCY = 0.03
_W_POPULARITY = 0.02

# Per-domain scores for each dimension (0–1)
_APP_RELEVANCE: dict[str, float] = {
    "Agentic AI": 1.0, "AI Coding": 1.0, "Production AI": 0.9,
    "AI Engineering": 0.9, "AI Architecture": 0.85, "Models": 0.7,
    "AI Applications": 0.6, "Industry": 0.3,
}
_PROD_USEFULNESS: dict[str, float] = {
    "Production AI": 1.0, "AI Coding": 0.85, "AI Engineering": 0.80,
    "Agentic AI": 0.75, "AI Architecture": 0.70, "Models": 0.55,
    "AI Applications": 0.45, "Industry": 0.25,
}
_ARCH_IMPACT: dict[str, float] = {
    "AI Architecture": 1.0, "Agentic AI": 0.75, "AI Engineering": 0.55,
    "Production AI": 0.50, "Models": 0.40, "AI Coding": 0.35,
    "AI Applications": 0.30, "Industry": 0.15,
}
_PRACTICALITY: dict[str, float] = {
    "AI Coding": 1.0, "AI Engineering": 0.90, "Production AI": 0.85,
    "Agentic AI": 0.70, "AI Architecture": 0.60, "Models": 0.40,
    "AI Applications": 0.50, "Industry": 0.20,
}
_LEARNING_VALUE_BY_TYPE: dict[str, float] = {
    "video": 1.0, "blog": 0.90, "podcast": 0.85, "newsletter": 0.75,
    "article": 0.65, "paper": 0.55, "social": 0.30, "discussion": 0.35,
}


def _relevance_score(item: FetchedItem, now: datetime) -> float:
    published = item.published_at
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (now - published).total_seconds() / 3600)
    recency = max(0.0, 1.0 - age_hours / 168.0)

    primary = item.domain_tags[0] if item.domain_tags else "Industry"
    app_relevance = _APP_RELEVANCE.get(primary, 0.30)
    prod_usefulness = _PROD_USEFULNESS.get(primary, 0.25)
    arch_impact = _ARCH_IMPACT.get(primary, 0.15)
    practicality = _PRACTICALITY.get(primary, 0.20)
    learning_value = _LEARNING_VALUE_BY_TYPE.get(item.content_type, 0.50)
    credibility = _SOURCE_CREDIBILITY.get(item.source_name, _DEFAULT_CREDIBILITY)
    novelty = recency  # proxy: newer content is more likely novel
    popularity = min(1.0, getattr(item, "social_score", 0.0))

    score = (
        _W_APP_RELEVANCE * app_relevance
        + _W_PROD_USEFULNESS * prod_usefulness
        + _W_LEARNING_VALUE * learning_value
        + _W_ARCH_IMPACT * arch_impact
        + _W_PRACTICALITY * practicality
        + _W_CREDIBILITY * credibility
        + _W_NOVELTY * novelty
        + _W_RECENCY * recency
        + _W_POPULARITY * popularity
    )
    return min(1.0, max(0.0, score))


def rank_and_cap(
    items: list[FetchedItem],
    max_per_domain: int = 10,
    max_per_source: int = 3,
) -> list[FetchedItem]:
    """Deduplicate by URL, ensure domain tags, score, and cap per domain and per source."""
    seen_urls: set[str] = set()
    unique: list[FetchedItem] = []
    for item in items:
        if item.source_url not in seen_urls:
            seen_urls.add(item.source_url)
            if not item.domain_tags:
                item.domain_tags = classify_domains(f"{item.title} {item.summary}")
            unique.append(item)

    now = datetime.now(timezone.utc)
    unique.sort(key=lambda i: _relevance_score(i, now), reverse=True)

    domain_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    result: list[FetchedItem] = []
    for item in unique:
        if not item.domain_tags:
            item.domain_tags = ["Industry"]
        primary = item.domain_tags[0]
        source = item.source_name
        if (
            domain_counts.get(primary, 0) < max_per_domain
            and source_counts.get(source, 0) < max_per_source
        ):
            domain_counts[primary] = domain_counts.get(primary, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            result.append(item)

    return result


def score_item(item: FetchedItem) -> float:
    return _relevance_score(item, datetime.now(timezone.utc))
