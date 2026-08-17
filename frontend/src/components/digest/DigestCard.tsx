import type { ContentType, DigestItem } from "@/lib/types";

const TYPE_CONFIG: Record<ContentType, { label: string; color: string }> = {
  podcast:     { label: "Podcast",    color: "bg-purple-100 text-purple-700" },
  video:       { label: "Video",      color: "bg-red-100 text-red-700" },
  article:     { label: "Article",    color: "bg-blue-100 text-blue-700" },
  blog:        { label: "Article",    color: "bg-blue-100 text-blue-700" },
  newsletter:  { label: "Newsletter", color: "bg-amber-100 text-amber-700" },
  discussion:  { label: "Discussion", color: "bg-green-100 text-green-700" },
  social:      { label: "Post",       color: "bg-sky-100 text-sky-700" },
  paper:       { label: "Paper",      color: "bg-slate-100 text-slate-700" },
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
  const typeConfig = TYPE_CONFIG[item.content_type] ?? { label: item.content_type, color: "bg-slate-100 text-slate-700" };

  return (
    <article className="py-5 border-b border-[#f1f5f9] last:border-0">
      <div className="flex gap-3">
        {/* Left: content */}
        <div className="flex-1 min-w-0">
          {/* Type badge */}
          <span className={`inline-block text-[10px] font-semibold tracking-[0.12em] uppercase px-2 py-0.5 rounded-full mb-2 ${typeConfig.color}`}>
            {typeConfig.label}
          </span>

          {/* Title */}
          {item.source_title && (
            <h3 className="text-[15px] font-semibold text-[#0f172a] leading-snug mb-2">
              {item.source_title}
            </h3>
          )}

          {/* Narrative */}
          <p className="text-[13px] leading-[1.7] text-[#475569] mb-3">
            {narrative}
          </p>

          {/* Source link */}
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-[12px] font-medium text-[#4f46e5] hover:text-[#4338ca] transition-colors"
          >
            {item.source_name}
            <svg width="9" height="9" viewBox="0 0 9 9" fill="none" aria-hidden="true">
              <path d="M1 8L8 1M8 1H2.5M8 1V6.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </a>
        </div>

        {/* Right: thumbnail */}
        {item.thumbnail_url && (
          <div className="shrink-0 self-start mt-1">
            <img
              src={item.thumbnail_url}
              alt=""
              width={88}
              height={66}
              className="w-[88px] h-[66px] object-cover rounded-lg border border-[#e2e8f0]"
              loading="lazy"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          </div>
        )}
      </div>
    </article>
  );
}
