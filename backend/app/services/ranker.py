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


def _relevance_score(item: FetchedItem, now: datetime) -> float:
    published = item.published_at
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (now - published).total_seconds() / 3600)
    recency = max(0.0, 1.0 - age_hours / 48.0)
    domain_match = min(1.0, len(item.domain_tags) * 0.3)
    return recency * 0.7 + domain_match * 0.3


def rank_and_cap(
    items: list[FetchedItem],
    max_per_domain: int = 10,
    max_per_source: int = 2,
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
