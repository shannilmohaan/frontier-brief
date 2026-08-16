import type { DigestItem } from "@/lib/types";
import { DigestCard } from "./DigestCard";

interface DigestSectionProps {
  domain: string;
  items: DigestItem[];
}

export function DigestSection({ domain, items }: DigestSectionProps) {
  return (
    <section>
      {/* Section header */}
      <div className="flex items-baseline justify-between pb-3 border-b border-[#1e293b] mb-1">
        <h2 className="text-[13px] font-bold text-[#f1f5f9] tracking-tight">
          {domain}
        </h2>
        <span className="text-[11px] text-[#334155] font-medium">
          {items.length}
        </span>
      </div>

      {/* Items */}
      <div>
        {items.map((item) => (
          <DigestCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
