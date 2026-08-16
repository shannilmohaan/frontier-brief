"use client";

import type { Domain } from "@/lib/types";

interface DomainFilterChipsProps {
  domains: Domain[];
  active: Domain | null;
  onSelect: (domain: Domain | null) => void;
}

export function DomainFilterChips({ domains, active, onSelect }: DomainFilterChipsProps) {
  return (
    <div
      role="group"
      aria-label="Filter by domain"
      className="flex gap-0 px-4 overflow-x-auto hide-scrollbar"
    >
      <TabButton active={active === null} onClick={() => onSelect(null)}>
        All
      </TabButton>
      {domains.map((domain) => (
        <TabButton
          key={domain}
          active={active === domain}
          onClick={() => onSelect(domain)}
        >
          {domain}
        </TabButton>
      ))}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={[
        "shrink-0 px-3 py-3 text-[12px] font-medium transition-all whitespace-nowrap border-b-2",
        "min-h-[44px]",
        active
          ? "text-[#f1f5f9] border-[#6366f1]"
          : "text-[#475569] border-transparent hover:text-[#94a3b8]",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
