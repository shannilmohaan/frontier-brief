"use client";

import { useState } from "react";
import type { DigestItem } from "@/lib/types";
import { BuildImpactBadgeLarge } from "@/components/digest/BuildImpactBadge";
import { ProductionReadinessPill } from "@/components/digest/ProductionReadinessPill";

const CONTENT_TYPE_LABELS: Record<string, string> = {
  video: "VIDEO",
  podcast: "PODCAST",
  paper: "PAPER",
  newsletter: "NEWSLETTER",
  blog: "ARTICLE",
  article: "ARTICLE",
};

function ExternalLinkIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true">
      <path d="M2 9L9 2M9 2H4M9 2V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function stripCitation(narrative: string): string {
  return narrative.replace(/\n\nSource:\s*\[.*?\]\(.*?\)\s*$/, "").trim();
}

function badgeStyle(contentType: string): React.CSSProperties {
  const map: Record<string, React.CSSProperties> = {
    video: { background: "var(--badge-video-bg)", color: "var(--badge-video-text)" },
    podcast: { background: "var(--badge-podcast-bg)", color: "var(--badge-podcast-text)" },
    newsletter: { background: "var(--badge-newsletter-bg)", color: "var(--badge-newsletter-text)" },
  };
  return map[contentType] ?? { background: "var(--badge-article-bg)", color: "var(--badge-article-text)" };
}

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function HeroCard({ item }: { item: DigestItem }) {
  const [imgError, setImgError] = useState(false);
  const typeLabel = CONTENT_TYPE_LABELS[item.content_type] ?? item.content_type.toUpperCase();
  const narrative = stripCitation(item.narrative);

  return (
    <article
      className="card-lift rounded-xl p-5 sm:p-7 mb-8"
      style={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }}
    >
      {/* Meta row */}
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <span
          className="text-[10px] font-semibold tracking-widest uppercase rounded-sm px-1.5 py-0.5 shrink-0"
          style={badgeStyle(item.content_type)}
        >
          {typeLabel}
        </span>
        <span className="text-[11px] shrink-0" style={{ color: "var(--text-muted)" }}>
          {item.source_name}
        </span>
        <span style={{ color: "var(--border-bright)" }}>·</span>
        <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
          {formatTimeAgo(item.created_at)}
        </span>
      </div>

      {/* Headline */}
      <h2
        className="text-[22px] sm:text-[28px] leading-tight mb-4"
        style={{ fontFamily: "var(--font-serif)", color: "var(--text-primary)" }}
      >
        {item.source_title || item.source_name}
      </h2>

      {/* Thumbnail */}
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
        <div className="mb-4 pl-4 py-1" style={{ borderLeft: "2px solid var(--accent)" }}>
          <p className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--accent)" }}>
            Why it matters for builders
          </p>
          <p className="text-[13px] leading-relaxed" style={{ color: "var(--text-primary)", fontStyle: "italic" }}>
            {item.why_it_matters}
          </p>
        </div>
      )}

      {/* What changed */}
      {item.what_changed && (
        <div className="mb-4 pl-4 py-1" style={{ borderLeft: "2px solid var(--accent-warm)" }}>
          <p className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--accent-warm)" }}>
            What changed
          </p>
          <p className="text-[13px] leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {item.what_changed}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between flex-wrap gap-3 mt-5 pt-4" style={{ borderTop: "1px solid var(--border-muted)" }}>
        <div className="flex items-center gap-2 flex-wrap">
          <BuildImpactBadgeLarge value={item.build_impact} />
          <ProductionReadinessPill value={item.production_readiness} />
          {item.who_should_care && (
            <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
              For: {item.who_should_care}
            </span>
          )}
        </div>
        <a
          href={item.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-[12px] font-medium px-3 py-2 rounded-lg transition-colors"
          style={{ color: "var(--accent)", border: "1px solid var(--border)" }}
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
