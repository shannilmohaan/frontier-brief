import type { BuildImpact } from "@/lib/types";

const CONFIG: Record<BuildImpact, { label: string; style: React.CSSProperties }> = {
  "Very High": {
    label: "🔥 Very High",
    style: { background: "rgba(239,68,68,0.14)", color: "#f87171", border: "1px solid rgba(239,68,68,0.25)" },
  },
  "High": {
    label: "▲ High",
    style: { background: "rgba(245,158,11,0.12)", color: "#fbbf24", border: "1px solid rgba(245,158,11,0.25)" },
  },
  "Medium": {
    label: "● Medium",
    style: { background: "rgba(59,130,246,0.10)", color: "#93c5fd", border: "1px solid rgba(59,130,246,0.20)" },
  },
  "Low": {
    label: "○ Low",
    style: { background: "rgba(100,116,139,0.10)", color: "#94a3b8", border: "1px solid rgba(100,116,139,0.20)" },
  },
  "Background": {
    label: "Background",
    style: { background: "transparent", color: "var(--text-muted)", border: "1px solid var(--border)" },
  },
};

interface BuildImpactBadgeProps {
  value: BuildImpact | null | undefined;
  size?: "sm" | "md";
}

export function BuildImpactBadge({ value, size = "sm" }: BuildImpactBadgeProps) {
  if (!value || value === "Background") return null;
  const { label, style } = CONFIG[value] ?? CONFIG["Medium"];
  const fontSize = size === "md" ? "11px" : "10px";
  return (
    <span
      className="inline-flex items-center font-semibold tracking-wide rounded-full px-2 py-0.5 shrink-0"
      style={{ ...style, fontSize }}
      aria-label={`Build Impact: ${value}`}
    >
      {label}
    </span>
  );
}

export function BuildImpactBadgeLarge({ value }: { value: BuildImpact | null | undefined }) {
  if (!value) return null;
  const { label, style } = CONFIG[value] ?? CONFIG["Medium"];
  return (
    <span
      className="inline-flex items-center gap-1 text-[12px] font-semibold tracking-wide rounded-lg px-3 py-1"
      style={style}
      aria-label={`Build Impact: ${value}`}
    >
      BUILD IMPACT · {label}
    </span>
  );
}
