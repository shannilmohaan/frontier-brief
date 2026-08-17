interface EmptyStateProps {
  title?: string;
  subtitle?: string;
  onRefresh?: () => void;
}

function RadarIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true" style={{ color: "var(--text-muted)" }}>
      <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" opacity="0.4" />
      <circle cx="20" cy="20" r="11" stroke="currentColor" strokeWidth="1" strokeDasharray="3 3" opacity="0.6" />
      <circle cx="20" cy="20" r="4" stroke="currentColor" strokeWidth="1.5" />
      <line x1="20" y1="20" x2="29" y2="11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
      <circle cx="20" cy="20" r="1.5" fill="currentColor" />
    </svg>
  );
}

export function EmptyState({
  title = "No developments yet",
  subtitle = "No significant AI developments to report yet.",
  onRefresh,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center gap-4">
      <RadarIcon />
      <div>
        <p className="text-[15px] font-medium mb-1" style={{ color: "var(--text-secondary)" }}>
          {title}
        </p>
        <p className="text-sm max-w-[260px]" style={{ color: "var(--text-muted)" }}>
          {subtitle}
        </p>
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          className="text-[12px] font-medium transition-colors"
          style={{ color: "var(--accent)" }}
        >
          Trigger a refresh →
        </button>
      )}
    </div>
  );
}
