import type { ProductionReadiness } from "@/lib/types";

const CONFIG: Record<ProductionReadiness, { style: React.CSSProperties }> = {
  "Experimental":     { style: { background: "rgba(239,68,68,0.10)",   color: "#fca5a5" } },
  "Preview":          { style: { background: "rgba(245,158,11,0.10)",  color: "#fcd34d" } },
  "Beta":             { style: { background: "rgba(59,130,246,0.10)",  color: "#93c5fd" } },
  "Production Ready": { style: { background: "rgba(34,197,94,0.10)",   color: "#86efac" } },
  "Enterprise Ready": { style: { background: "rgba(16,185,129,0.12)",  color: "#6ee7b7" } },
  "N/A":              { style: { display: "none" } },
};

interface ProductionReadinessPillProps {
  value: ProductionReadiness | null | undefined;
}

export function ProductionReadinessPill({ value }: ProductionReadinessPillProps) {
  if (!value || value === "N/A") return null;
  const { style } = CONFIG[value] ?? CONFIG["N/A"];
  return (
    <span
      className="inline-flex items-center text-[9px] font-medium tracking-wide rounded-full px-1.5 py-0.5 shrink-0"
      style={style}
      aria-label={`Production readiness: ${value}`}
    >
      {value}
    </span>
  );
}
