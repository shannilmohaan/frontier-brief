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

function ImportanceDots({ value }: { value: number }) {
  const clamped = Math.max(1, Math.min(5, value));
  return (
    <div className="flex items-center gap-0.5" aria-label={`Importance ${clamped} of 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          style={{
            color: i < clamped ? "var(--accent-warm)" : "var(--border-bright)",
          }}
          className={i < clamped && clamped >= 4 ? "animate-pulse" : ""}
        >
          ●
        </span>
      ))}
    </div>
  );
}

function ExternalLinkIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true">
      <path d="M2 9L9 2M9 2H4M9 2V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// Strip the appended "Source: [name](url)" from the narrative
function stripCitation(narrative: string): string {
  return narrative.replace(/\n\nSource:\s*\[.*?\]\(.*?\)\s*$/, "").trim();
}

export function HeroCard({ item }: { item: DigestItem }) {
  const [imgError, setImgError] = useState(false);
  const label = credibilityLabel(item.source_name, item.content_type);
  const typeLabel = CONTENT_TYPE_LABELS[item.content_type] ?? item.content_type.toUpperCase();
  const narrative = stripCitation(item.narrative);
  const timeAgo = formatTimeAgo(item.created_at);

  return (
    <article
      className="card-lift rounded-xl p-5 sm:p-7 mb-8"
      style={{
        background: "var(--surface-raised)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Top meta row */}
      <div className="flex items-center justify-between mb-4 gap-2 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className="text-[10px] font-semibold tracking-widest uppercase rounded-sm px-1.5 py-0.5"
            style={badgeStyle(item.content_type)}
          >
            {typeLabel}
          </span>
          <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
            {item.source_name}
          </span>
          <span style={{ color: "var(--border-bright)" }}>·</span>
          <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
            {timeAgo}
          </span>
        </div>
        <CredibilityPill label={label} />
      </div>

      {/* Headline */}
      <h2
        className="text-[22px] sm:text-[28px] leading-tight mb-4"
        style={{ fontFamily: "var(--font-serif)", color: "var(--text-primary)" }}
      >
        {item.source_title || item.source_name}
      </h2>

      {/* Thumbnail (if available) */}
      {item.thumbnail_url && !imgError && (
        <div className="mb-4 rounded-lg overflow-hidden" style={{ border: "1px solid var(--border)" }}>
          <img
            src={item.thumbnail_url}
            alt=""
            className="w-full max-h-52 object-cover"
            loading="lazy"
            onError={() => setImgError(true)}
          />
        </div>
      )}

      {/* Narrative */}
      <p className="text-[14px] leading-relaxed mb-4" style={{ color: "var(--text-secondary)" }}>
        {narrative}
      </p>

      {/* Why it matters */}
      {item.why_it_matters && (
        <div
          className="mb-5 pl-4 py-1"
          style={{ borderLeft: "2px solid var(--accent)" }}
        >
          <p className="text-[11px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--accent)" }}>
            Why it matters
          </p>
          <p className="text-[13px] leading-relaxed" style={{ color: "var(--text-primary)", fontStyle: "italic" }}>
            {item.why_it_matters}
          </p>
        </div>
      )}

      {/* Footer row */}
      <div className="flex items-center justify-between mt-2 flex-wrap gap-3">
        <ImportanceDots value={item.importance} />
        <a
          href={item.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-[12px] font-medium px-3 py-2 rounded-lg transition-colors"
          style={{
            color: "var(--accent)",
            border: "1px solid var(--border)",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--accent-dim)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border)";
          }}
        >
          Read original
          <ExternalLinkIcon />
        </a>
      </div>
    </article>
  );
}

function CredibilityPill({ label }: { label: string }) {
  const styles: Record<string, React.CSSProperties> = {
    "Primary Source": { background: "rgba(91,138,240,0.12)", color: "#93c5fd" },
    "Peer Reviewed": { background: "rgba(34,197,94,0.10)", color: "#86efac" },
    "Expert Curation": { background: "rgba(245,158,11,0.10)", color: "#fcd34d" },
    "Expert Analysis": { background: "rgba(168,85,247,0.10)", color: "#c4b5fd" },
    "Community Signal": { background: "rgba(100,116,139,0.12)", color: "#94a3b8" },
  };
  return (
    <span
      className="text-[10px] font-medium tracking-wide rounded-full px-2 py-0.5"
      style={styles[label] ?? styles["Community Signal"]}
    >
      {label}
    </span>
  );
}

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

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
