import type { BuildImpact } from "@/lib/types";

const CONFIG: Record<BuildImpact, { label: string; style: React.CSSProperties }> = {
  "Very High": {
    label: "🔥 Very High",
    style: { background: "#fee2e2", color: "#991b1b", border: "1px solid #fecaca" },
  },
  "High": {
    label: "▲ High",
    style: { background: "#fef3c7", color: "#92400e", border: "1px solid #fde68a" },
  },
  "Medium": {
    label: "● Medium",
    style: { background: "#dbeafe", color: "#1e40af", border: "1px solid #bfdbfe" },
  },
  "Low": {
    label: "○ Low",
    style: { background: "#f1f5f9", color: "#475569", border: "1px solid #e2e8f0" },
  },
  "Background": {
    label: "Background",
    style: { background: "#f1f5f9", color: "#94a3b8", border: "1px solid #e2e8f0" },
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
