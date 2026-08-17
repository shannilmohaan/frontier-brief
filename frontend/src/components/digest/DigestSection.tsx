import type { DigestItem } from "@/lib/types";
import { DigestCard } from "./DigestCard";

interface DigestSectionProps {
  domain: string;
  items: DigestItem[];
}

export function DigestSection({ domain, items }: DigestSectionProps) {
  return (
    <section>
      <div className="flex items-baseline justify-between pb-3 border-b-2 border-[#0f172a] mb-1">
        <h2 className="text-[13px] font-bold text-[#0f172a] tracking-tight uppercase">
          {domain}
        </h2>
        <span className="text-[11px] text-[#94a3b8] font-medium">
          {items.length}
        </span>
      </div>
      <div>
        {items.map((item) => (
          <DigestCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
