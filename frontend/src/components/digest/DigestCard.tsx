import type { ContentType, DigestItem } from "@/lib/types";

const CONTENT_TYPE_LABEL: Record<ContentType, string> = {
  video:       "Video",
  paper:       "Paper",
  newsletter:  "Newsletter",
  blog:        "Blog",
  social:      "Post",
  discussion:  "Discussion",
};

function stripCitation(narrative: string): string {
  const idx = narrative.lastIndexOf("\n\nSource:");
  return idx !== -1 ? narrative.slice(0, idx).trim() : narrative.trim();
}

interface DigestCardProps {
  item: DigestItem;
}

export function DigestCard({ item }: DigestCardProps) {
  const narrative = stripCitation(item.narrative);
  const typeLabel = CONTENT_TYPE_LABEL[item.content_type] ?? item.content_type;

  return (
    <article className="py-5 border-b border-[#1a2540] last:border-0">
      {/* Type label */}
      <p className="text-[10px] font-semibold tracking-[0.14em] uppercase text-[#4a5568] mb-2">
        {typeLabel}
      </p>

      {/* Title */}
      {item.source_title && (
        <h3 className="text-[16px] font-semibold text-[#e2e8f0] leading-snug mb-2.5">
          {item.source_title}
        </h3>
      )}

      {/* Narrative */}
      <p className="text-[13px] leading-[1.75] text-[#64748b] mb-3">
        {narrative}
      </p>

      {/* Source */}
      <a
        href={item.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-[12px] font-medium text-[#6366f1] hover:text-[#818cf8] transition-colors"
      >
        {item.source_name}
        <svg width="9" height="9" viewBox="0 0 9 9" fill="none" aria-hidden="true">
          <path d="M1 8L8 1M8 1H2.5M8 1V6.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </a>
    </article>
  );
}
