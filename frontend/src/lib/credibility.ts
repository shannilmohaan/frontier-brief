export type CredibilityLabel = "Primary Source" | "Peer Reviewed" | "Expert Curation" | "Expert Analysis" | "Community Signal";

const PRIMARY_SOURCES = new Set([
  "OpenAI Blog", "Anthropic Blog", "Google DeepMind Blog", "Meta AI Blog",
  "Microsoft AI Blog", "NVIDIA Blog", "Mistral AI Blog", "xAI Blog",
]);

const EXPERT_CURATION = new Set([
  "The Batch", "Import AI", "Ahead of AI", "Interconnects",
  "Latent Space", "One Useful Thing", "The Gradient", "Last Week in AI",
  "Ben's Bites", "TLDR AI",
]);

export function credibilityLabel(sourceName: string, contentType: string): CredibilityLabel {
  if (PRIMARY_SOURCES.has(sourceName)) return "Primary Source";
  if (contentType === "paper") return "Peer Reviewed";
  if (EXPERT_CURATION.has(sourceName)) return "Expert Curation";
  if (contentType === "podcast" || contentType === "video") return "Expert Analysis";
  return "Community Signal";
}
