import type { ContentType, DigestItem, Domain } from "@/lib/types";
import { SourceLink } from "./SourceLink";

const DOMAIN_COLORS: Record<Domain, { bg: string; text: string }> = {
  "Agentic AI":                  { bg: "#EEF2FF", text: "#4338CA" },
  "New Model Capabilities":      { bg: "#EFF6FF", text: "#1D4ED8" },
  "Context Management":          { bg: "#F0FDFA", text: "#0F766E" },
  "Token Economics":             { bg: "#F0FDF4", text: "#15803D" },
  "Tool Use & Function Calling": { bg: "#FFF7ED", text: "#C2410C" },
  "AI Coding Agents":            { bg: "#F5F3FF", text: "#6D28D9" },
  "Reasoning & Planning":        { bg: "#FFFBEB", text: "#B45309" },
  "Agent Memory & Persistence":  { bg: "#FFF1F2", text: "#BE123C" },
  "Applied AI Engineering":      { bg: "#F1F5F9", text: "#475569" },
  "AI Research":                 { bg: "#F8FAFC", text: "#334155" },
};

const CONTENT_TYPE_LABELS: Record<ContentType, string> = {
  video:       "Video",
  paper:       "Paper",
  newsletter:  "Newsletter",
  blog:        "Blog",
  social:      "Social",
  discussion:  "Discussion",
};

const DEFAULT_DOMAIN_COLOR = { bg: "#F1F5F9", text: "#475569" };

function stripCitation(narrative: string): string {
  const idx = narrative.lastIndexOf("\n\nSource:");
  return idx !== -1 ? narrative.slice(0, idx).trim() : narrative.trim();
}

interface DigestCardProps {
  item: DigestItem;
}

export function DigestCard({ item }: DigestCardProps) {
  const primaryDomain = (item.domain_tags[0] ?? "AI Research") as Domain;
  const domainColor = DOMAIN_COLORS[primaryDomain] ?? DEFAULT_DOMAIN_COLOR;
  const narrative = stripCitation(item.narrative);
  const contentLabel = CONTENT_TYPE_LABELS[item.content_type] ?? item.content_type;

  return (
    <article className="bg-white rounded-2xl border border-[#E8EAED] p-5 transition-colors hover:border-[#D1D5DB]">
      <h3 className="sr-only">{item.source_name}</h3>

      <div className="flex items-start justify-between gap-2 mb-3">
        <span
          className="text-[11px] font-semibold px-2.5 py-1 rounded-full leading-none"
          style={{ backgroundColor: domainColor.bg, color: domainColor.text }}
        >
          {primaryDomain}
        </span>
        <span className="text-[11px] font-medium text-[#94A3B8] bg-[#F8F9FA] px-2.5 py-1 rounded-full whitespace-nowrap leading-none shrink-0">
          {contentLabel}
        </span>
      </div>

      <p className="text-[15px] leading-[1.7] text-[#475569] mb-3">{narrative}</p>

      <SourceLink href={item.source_url}>{item.source_name}</SourceLink>
    </article>
  );
}
