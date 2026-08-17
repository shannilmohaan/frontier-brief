from datetime import datetime, timezone

from app.services.fetchers.base import FetchedItem

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Agentic AI": [
        "agent", "agentic", "autonomous agent", "multi-agent", "agent framework",
        "llm agent", "ai agent", "agentic workflow", "self-improving",
    ],
    "New Model Capabilities": [
        "gpt-4", "gpt-5", "claude 3", "claude 4", "gemini", "llama", "mistral",
        "phi-", "qwen", "model release", "new model", "multimodal", "vision model",
        "foundation model", "language model",
    ],
    "Context Management": [
        "context window", "long context", "context length", "retrieval augmented",
        "retrieval-augmented", "rag", "128k", "context size", "infinite context",
    ],
    "Token Economics": [
        "token cost", "pricing", "cost per token", "token efficiency", "compression",
        "quantization", "cheaper inference", "token budget", "inference cost",
    ],
    "Tool Use & Function Calling": [
        "tool use", "tool calling", "function calling", "tool call", "plugins",
        "computer use", "mcp", "model context protocol", "api calling",
    ],
    "AI Coding Agents": [
        "coding agent", "code generation", "devin", "cursor", "copilot",
        "swe-bench", "software engineering agent", "ai coder", "code agent",
        "automated coding", "ai programming", "github copilot",
    ],
    "Reasoning & Planning": [
        "reasoning", "chain of thought", "cot", "planning", "o1", "o3", "r1",
        "thinking model", "step-by-step", "logical reasoning", "tree of thought",
        "self-reflection", "inference-time compute",
    ],
    "Agent Memory & Persistence": [
        "memory", "long-term memory", "episodic memory", "persistence",
        "memory module", "agent memory", "external memory", "memory augmented",
    ],
    "Applied AI Engineering": [
        "deployment", "production", "mlops", "inference", "latency", "throughput",
        "fine-tuning", "finetuning", "serving", "vllm", "ollama", "local llm",
        "edge deployment", "batch inference", "triton",
    ],
    "AI Research": [
        "paper", "research", "arxiv", "study", "experiment", "dataset", "evaluation",
        "empirical", "ablation", "benchmark", "proposed method", "we propose",
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


# Source credibility tier (0.0–1.0). Used as a 10% weight modifier.
# Tier 1: official lab blogs, peer-reviewed papers → 1.0
# Tier 2: expert curated newsletters / podcasts → 0.75–0.85
# Tier 3: general web / unknown → 0.5 (default)
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


_TYPE_BOOST: dict[str, float] = {
    "podcast": 0.1,
    "video": 0.05,
    "article": 0.0,
    "newsletter": 0.0,
    "blog": 0.0,
    "discussion": -0.05,
    "social": -0.05,
    "paper": 0.0,
}


def _relevance_score(item: FetchedItem, now: datetime) -> float:
    published = item.published_at
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (now - published).total_seconds() / 3600)
    recency = max(0.0, 1.0 - age_hours / 168.0)  # 7-day decay window
    domain_match = min(1.0, len(item.domain_tags) * 0.3)
    social = getattr(item, "social_score", 0.0)
    type_boost = _TYPE_BOOST.get(item.content_type, 0.0)
    credibility = _SOURCE_CREDIBILITY.get(item.source_name, _DEFAULT_CREDIBILITY)
    base = social * 0.35 + recency * 0.30 + domain_match * 0.25
    raw = base + type_boost * 0.10
    # Credibility adjusts final score by up to ±10%: credibility=1.0 → ×1.0, credibility=0.5 → ×0.95
    credibility_factor = 0.90 + 0.10 * credibility
    return min(1.0, max(0.0, raw * credibility_factor))


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
            item.domain_tags = ["AI Research"]
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
