import type { ProductionReadiness } from "@/lib/types";

const CONFIG: Record<ProductionReadiness, { style: React.CSSProperties }> = {
  "Experimental":     { style: { background: "#fee2e2", color: "#991b1b" } },
  "Preview":          { style: { background: "#fef3c7", color: "#92400e" } },
  "Beta":             { style: { background: "#dbeafe", color: "#1e40af" } },
  "Production Ready": { style: { background: "#dcfce7", color: "#166534" } },
  "Enterprise Ready": { style: { background: "#d1fae5", color: "#065f46" } },
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
