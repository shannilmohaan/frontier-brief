import type { DigestItem } from "@/lib/types";
import { DigestCard } from "./DigestCard";

interface DigestSectionProps {
  domain: string;
  items: DigestItem[];
}

export function DigestSection({ domain, items }: DigestSectionProps) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-3">
        <h2 className="text-[11px] font-semibold tracking-[0.12em] uppercase text-[#475569]">
          {domain}
        </h2>
        <span className="text-[11px] text-[#334155] font-medium">
          {items.length}
        </span>
        <div className="flex-1 h-px bg-[#1e293b]" />
      </div>
      <div className="flex flex-col gap-2.5">
        {items.map((item) => (
          <DigestCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
