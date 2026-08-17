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
      style={
        active
          ? { color: "var(--accent)", borderBottom: "2px solid var(--accent)" }
          : { color: "var(--text-muted)", borderBottom: "2px solid transparent" }
      }
      className="shrink-0 px-3 py-3 text-[12px] font-medium transition-all whitespace-nowrap min-h-[44px]"
      onMouseEnter={(e) => {
        if (!active) (e.currentTarget as HTMLButtonElement).style.color = "var(--text-secondary)";
      }}
      onMouseLeave={(e) => {
        if (!active) (e.currentTarget as HTMLButtonElement).style.color = "var(--text-muted)";
      }}
    >
      {children}
    </button>
  );
}
