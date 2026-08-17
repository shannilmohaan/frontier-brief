"use client";

import { useState } from "react";
import type { DigestItem } from "@/lib/types";
import { credibilityLabel } from "@/lib/credibility";

const CONTENT_TYPE_LABELS: Record<string, string> = {
  video: "VIDEO",
  podcast: "PODCAST",
  paper: "PAPER",
  newsletter: "NEWSLETTER",
  blog: "ARTICLE",
  article: "ARTICLE",
  social: "SOCIAL",
  discussion: "DISCUSSION",
};

function badgeStyle(contentType: string): React.CSSProperties {
  const map: Record<string, React.CSSProperties> = {
    video: { background: "var(--badge-video-bg)", color: "var(--badge-video-text)" },
    podcast: { background: "var(--badge-podcast-bg)", color: "var(--badge-podcast-text)" },
    paper: { background: "var(--badge-paper-bg)", color: "var(--badge-paper-text)" },
    newsletter: { background: "var(--badge-newsletter-bg)", color: "var(--badge-newsletter-text)" },
    social: { background: "var(--badge-social-bg)", color: "var(--badge-social-text)" },
    discussion: { background: "var(--badge-discussion-bg)", color: "var(--badge-discussion-text)" },
  };
  return map[contentType] ?? { background: "var(--badge-article-bg)", color: "var(--badge-article-text)" };
}

function ImportanceDots({ value }: { value: number }) {
  const clamped = Math.max(1, Math.min(5, value));
  return (
    <div className="flex items-center gap-0.5" aria-label={`Importance ${clamped} of 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className="text-[8px]"
          style={{ color: i < clamped ? "var(--accent-warm)" : "var(--border-bright)" }}
        >
          ●
        </span>
      ))}
    </div>
  );
}

function ExternalLinkIcon() {
  return (
    <svg width="9" height="9" viewBox="0 0 9 9" fill="none" aria-hidden="true">
      <path d="M1.5 7.5L7.5 1.5M7.5 1.5H3M7.5 1.5V6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function stripCitation(narrative: string): string {
  return narrative.replace(/\n\nSource:\s*\[.*?\]\(.*?\)\s*$/, "").trim();
}

function CredibilityPill({ label }: { label: string }) {
  const styles: Record<string, React.CSSProperties> = {
    "Primary Source": { background: "rgba(91,138,240,0.10)", color: "#7baaf7" },
    "Peer Reviewed": { background: "rgba(34,197,94,0.08)", color: "#6ee7b7" },
    "Expert Curation": { background: "rgba(245,158,11,0.08)", color: "#d4a04a" },
    "Expert Analysis": { background: "rgba(168,85,247,0.08)", color: "#a78bfa" },
    "Community Signal": { background: "rgba(100,116,139,0.10)", color: "var(--text-muted)" },
  };
  return (
    <span
      className="text-[9px] font-medium tracking-wide rounded-full px-1.5 py-0.5"
      style={styles[label] ?? styles["Community Signal"]}
    >
      {label}
    </span>
  );
}

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function DigestCard({ item }: { item: DigestItem }) {
  const [imgError, setImgError] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const label = credibilityLabel(item.source_name, item.content_type);
  const typeLabel = CONTENT_TYPE_LABELS[item.content_type] ?? item.content_type.toUpperCase();
  const isEditorial = item.content_type === "video" || item.content_type === "podcast";
  const narrative = stripCitation(item.narrative);

  return (
    <article className="py-5 border-b" style={{ borderColor: "var(--border-muted)" }}>
      <div className="flex gap-3">
        {/* Left: content */}
        <div className="flex-1 min-w-0">
          {/* Top row: type badge + credibility */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span
              className="text-[9px] font-semibold tracking-widest uppercase rounded-sm px-1.5 py-0.5"
              style={badgeStyle(item.content_type)}
            >
              {typeLabel}
            </span>
            <CredibilityPill label={label} />
          </div>

          {/* Title */}
          <h3
            className="text-[14px] font-semibold leading-snug mb-2"
            style={{
              color: "var(--text-primary)",
              fontFamily: isEditorial ? "var(--font-serif)" : "var(--font-sans)",
              fontSize: isEditorial ? "15px" : "14px",
            }}
          >
            {item.source_title || item.source_name}
          </h3>

          {/* Narrative */}
          <p className="text-[13px] leading-relaxed mb-2" style={{ color: "var(--text-secondary)", lineHeight: 1.7 }}>
            {narrative}
          </p>

          {/* Why it matters */}
          {item.why_it_matters && (
            <div className="mb-3">
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider mb-1 transition-colors"
                style={{ color: "var(--accent)", background: "none", border: "none", cursor: "pointer", padding: 0 }}
                aria-expanded={expanded}
              >
                <span
                  className="inline-block transition-transform duration-150"
                  style={{ transform: expanded ? "rotate(90deg)" : "rotate(0deg)" }}
                >
                  ›
                </span>
                Why it matters
              </button>
              {expanded && (
                <p
                  className="text-[12px] leading-relaxed pl-3"
                  style={{
                    color: "var(--text-primary)",
                    borderLeft: "2px solid var(--accent)",
                    fontStyle: "italic",
                  }}
                >
                  {item.why_it_matters}
                </p>
              )}
            </div>
          )}

          {/* Footer: source link + meta */}
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2">
              <a
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-[12px] font-medium transition-colors"
                style={{ color: "var(--accent)" }}
                onMouseEnter={(e) => ((e.currentTarget as HTMLAnchorElement).style.color = "var(--text-primary)")}
                onMouseLeave={(e) => ((e.currentTarget as HTMLAnchorElement).style.color = "var(--accent)")}
              >
                {item.source_name}
                <ExternalLinkIcon />
              </a>
              <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                {formatTimeAgo(item.created_at)}
              </span>
            </div>
            <ImportanceDots value={item.importance} />
          </div>
        </div>

        {/* Right: thumbnail */}
        {item.thumbnail_url && !imgError && (
          <div className="shrink-0 self-start">
            <img
              src={item.thumbnail_url}
              alt=""
              width={100}
              height={72}
              className="rounded-lg object-cover"
              style={{ border: "1px solid var(--border)", minWidth: "100px" }}
              loading="lazy"
              onError={() => setImgError(true)}
            />
          </div>
        )}
      </div>
    </article>
  );
}
