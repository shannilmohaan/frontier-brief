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
      className="flex gap-2 px-4 py-3 overflow-x-auto hide-scrollbar"
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
        "shrink-0 px-4 rounded-full text-[13px] font-medium transition-colors whitespace-nowrap",
        "min-h-[44px] min-w-[44px]",
        active
          ? "bg-[#0F172A] text-white"
          : "bg-white border border-[#E8EAED] text-[#475569] hover:border-[#D1D5DB]",
      ].join(" ")}
    >
      {children}
    </button>
  );
}
