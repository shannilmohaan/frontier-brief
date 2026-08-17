"use client";

import { useState } from "react";
import type { DigestItem } from "@/lib/types";
import { BuildImpactBadge } from "@/components/digest/BuildImpactBadge";
import { ProductionReadinessPill } from "@/components/digest/ProductionReadinessPill";

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

function ShouldIUseBadge({ value }: { value: string | null | undefined }) {
  if (!value || value === "Watch") return null;
  const styles: Record<string, React.CSSProperties> = {
    "Adopt":      { background: "#dcfce7", color: "#166534" },
    "Evaluate":   { background: "#dbeafe", color: "#1e40af" },
    "Experiment": { background: "#fef3c7", color: "#92400e" },
  };
  return (
    <span
      className="text-[9px] font-semibold uppercase tracking-wider rounded-full px-1.5 py-0.5"
      style={styles[value] ?? {}}
    >
      {value}
    </span>
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

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function DigestCard({ item }: { item: DigestItem }) {
  const [imgError, setImgError] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const typeLabel = CONTENT_TYPE_LABELS[item.content_type] ?? item.content_type.toUpperCase();
  const isEditorial = item.content_type === "video" || item.content_type === "podcast";
  const narrative = stripCitation(item.narrative);

  return (
    <article className="py-5 border-b" style={{ borderColor: "var(--border-muted)" }}>
      <div className="flex gap-3">
        {/* Left: content */}
        <div className="flex-1 min-w-0">
          {/* Top row: type badge + build impact + production readiness */}
          <div className="flex items-center gap-1.5 mb-2 flex-wrap">
            <span
              className="text-[9px] font-semibold tracking-widest uppercase rounded-sm px-1.5 py-0.5 shrink-0"
              style={badgeStyle(item.content_type)}
            >
              {typeLabel}
            </span>
            <BuildImpactBadge value={item.build_impact} />
            <ProductionReadinessPill value={item.production_readiness} />
          </div>

          {/* Title — clickable link to original */}
          <h3
            className="text-[14px] font-semibold leading-snug mb-2"
            style={{
              fontFamily: isEditorial ? "var(--font-serif)" : "var(--font-sans)",
              fontSize: isEditorial ? "15px" : "14px",
            }}
          >
            <a
              href={item.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline underline-offset-2"
              style={{ color: "var(--text-primary)", textDecorationColor: "var(--border-bright)" }}
            >
              {item.source_title || item.source_name}
            </a>
          </h3>

          {/* Narrative */}
          <p className="text-[13px] leading-relaxed mb-2" style={{ color: "var(--text-secondary)", lineHeight: 1.7 }}>
            {narrative}
          </p>

          {/* Why it matters (expandable) */}
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
                <div>
                  <p
                    className="text-[12px] leading-relaxed pl-3 mb-2"
                    style={{ color: "var(--text-primary)", borderLeft: "2px solid var(--accent)", fontStyle: "italic" }}
                  >
                    {item.why_it_matters}
                  </p>
                  {item.what_changed && (
                    <p className="text-[11px] pl-3" style={{ color: "var(--text-muted)", borderLeft: "2px solid var(--accent-warm)" }}>
                      <span style={{ color: "var(--accent-warm)", fontWeight: 600 }}>Changed: </span>
                      {item.what_changed}
                    </p>
                  )}
                  {item.who_should_care && (
                    <p className="text-[10px] mt-1 pl-3" style={{ color: "var(--text-muted)" }}>
                      For: {item.who_should_care}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Footer: source name (plain) + time + should_i_use */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[12px] font-medium" style={{ color: "var(--text-muted)" }}>
              {item.source_name}
            </span>
            <ShouldIUseBadge value={item.should_i_use} />
            <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              {formatTimeAgo(item.created_at)}
            </span>
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
