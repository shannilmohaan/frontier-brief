import type { DigestItem } from "@/lib/types";
import { DigestCard } from "./DigestCard";

interface DigestSectionProps {
  domain: string;
  items: DigestItem[];
}

export function DigestSection({ domain, items }: DigestSectionProps) {
  return (
    <section>
      <div
        className="flex items-center mb-1 pt-2"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <h2
          className="text-[11px] font-semibold tracking-widest uppercase py-3"
          style={{ color: "var(--text-muted)", fontVariant: "small-caps" }}
        >
          {domain}
        </h2>
      </div>
      <div>
        {items.map((item) => (
          <DigestCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
