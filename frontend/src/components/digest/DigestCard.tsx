import type { ContentType, DigestItem, Domain } from "@/lib/types";
import { SourceLink } from "./SourceLink";

const DOMAIN_COLORS: Record<Domain, { bg: string; text: string }> = {
  "Agentic AI":                  { bg: "#1e1b4b", text: "#a5b4fc" },
  "New Model Capabilities":      { bg: "#172554", text: "#93c5fd" },
  "Context Management":          { bg: "#022c22", text: "#6ee7b7" },
  "Token Economics":             { bg: "#052e16", text: "#86efac" },
  "Tool Use & Function Calling": { bg: "#431407", text: "#fdba74" },
  "AI Coding Agents":            { bg: "#2e1065", text: "#c4b5fd" },
  "Reasoning & Planning":        { bg: "#451a03", text: "#fcd34d" },
  "Agent Memory & Persistence":  { bg: "#4c0519", text: "#fda4af" },
  "Applied AI Engineering":      { bg: "#0f172a", text: "#94a3b8" },
  "AI Research":                 { bg: "#0f172a", text: "#64748b" },
};

const CONTENT_TYPE_ICONS: Record<ContentType, string> = {
  video:       "▶",
  paper:       "◎",
  newsletter:  "✉",
  blog:        "✦",
  social:      "◈",
  discussion:  "◉",
};

const DEFAULT_DOMAIN_COLOR = { bg: "#1e293b", text: "#94a3b8" };

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
  const icon = CONTENT_TYPE_ICONS[item.content_type] ?? "◆";

  return (
    <article className="group bg-[#1e293b] rounded-xl border border-[#334155] p-4 transition-all hover:border-[#475569] hover:bg-[#263347]">
      {/* Top row: domain pill + type icon */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <span
          className="text-[11px] font-semibold px-2.5 py-1 rounded-full leading-none tracking-wide"
          style={{ backgroundColor: domainColor.bg, color: domainColor.text }}
        >
          {primaryDomain}
        </span>
        <span className="text-[12px] text-[#475569]" aria-label={item.content_type}>
          {icon}
        </span>
      </div>

      {/* Title */}
      {item.source_title && (
        <h3 className="text-[15px] font-semibold text-[#f1f5f9] leading-snug mb-2 line-clamp-3">
          {item.source_title}
        </h3>
      )}

      {/* Narrative */}
      <p className="text-[13px] leading-relaxed text-[#94a3b8] mb-3">
        {narrative}
      </p>

      {/* Source link */}
      <SourceLink href={item.source_url}>{item.source_name}</SourceLink>
    </article>
  );
}
