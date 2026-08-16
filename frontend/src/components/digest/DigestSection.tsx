import type { DigestItem } from "@/lib/types";
import { DigestCard } from "./DigestCard";

interface DigestSectionProps {
  domain: string;
  items: DigestItem[];
}

export function DigestSection({ domain, items }: DigestSectionProps) {
  return (
    <section>
      <h2 className="text-[11px] font-semibold tracking-widest uppercase text-[#94A3B8] mb-3">
        {domain}
      </h2>
      <div className="flex flex-col gap-3">
        {items.map((item) => (
          <DigestCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
