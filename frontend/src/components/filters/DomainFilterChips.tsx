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
      className="flex gap-2 px-4 py-2.5 overflow-x-auto hide-scrollbar"
    >
      <ChipButton active={active === null} onClick={() => onSelect(null)}>
        All
      </ChipButton>

      {domains.map((domain) => (
        <ChipButton
          key={domain}
          active={active === domain}
          onClick={() => onSelect(domain)}
        >
          {domain}
        </ChipButton>
      ))}
    </div>
  );
}

function ChipButton({
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
        "shrink-0 px-3.5 rounded-full text-[12px] font-medium transition-all whitespace-nowrap",
        "min-h-[34px]",
        active
          ? "bg-[#6366f1] text-white"
          : "bg-[#1e293b] border border-[#334155] text-[#64748b] hover:border-[#475569] hover:text-[#94a3b8]",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
