"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { DomainFilterChips } from "@/components/filters/DomainFilterChips";
import { DigestSection } from "@/components/digest/DigestSection";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { fetchLatestDigest, pollRefreshStatus, triggerRefresh } from "@/lib/api";
import type { DigestItem, Domain } from "@/lib/types";

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function RefreshIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
      <path
        d="M12.5 2.5A6 6 0 1 1 7.5 1.5M12.5 2.5V5.5M12.5 2.5H9.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function Home() {
  const [items, setItems] = useState<DigestItem[]>([]);
  const [activeDomain, setActiveDomain] = useState<Domain | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const loadDigest = useCallback(async () => {
    try {
      const data = await fetchLatestDigest();
      if (!mountedRef.current) return;
      setItems(data.items);
      if (data.items.length > 0) {
        const latest = data.items.reduce((a, b) =>
          a.created_at > b.created_at ? a : b
        );
        setLastUpdated(latest.created_at);
      }
      setError(null);
    } catch {
      if (!mountedRef.current) return;
      setError("Could not load digest.");
    } finally {
      if (mountedRef.current) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDigest();
  }, [loadDigest]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setError(null);
    let finished = false;
    try {
      const { job_id } = await triggerRefresh();
      const deadline = Date.now() + 120_000;
      while (Date.now() < deadline) {
        if (!mountedRef.current) return;
        await new Promise((r) => setTimeout(r, 4_000));
        if (!mountedRef.current) return;
        const { status } = await pollRefreshStatus(job_id);
        if (status === "completed") {
          finished = true;
          await loadDigest();
          break;
        }
        if (status === "failed") {
          finished = true;
          if (mountedRef.current) setError("Refresh failed. Please try again.");
          break;
        }
      }
      if (!finished && mountedRef.current) {
        setError("Still processing — check back in a minute.");
      }
    } catch {
      if (mountedRef.current) setError("Refresh failed. Please try again.");
    } finally {
      if (mountedRef.current) setIsRefreshing(false);
    }
  };

  const domains = Array.from(
    new Set(items.flatMap((item) => item.domain_tags).filter(Boolean) as Domain[])
  );

  const filteredItems = activeDomain
    ? items.filter((item) => item.domain_tags.includes(activeDomain))
    : items;

  const grouped = filteredItems.reduce<Record<string, DigestItem[]>>(
    (acc, item) => {
      const domain = item.domain_tags[0] ?? "AI Research";
      acc[domain] = [...(acc[domain] ?? []), item];
      return acc;
    },
    {}
  );

  return (
    <div className="min-h-screen bg-[#0f172a]">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-[#0a0f1e]/95 backdrop-blur-md border-b border-[#1e293b]">
        <div className="max-w-[680px] mx-auto px-4 h-[52px] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="text-[16px] font-bold tracking-tight text-[#f1f5f9]">
              Frontier Brief
            </span>
            <span className="hidden sm:block text-[11px] text-[#334155] font-medium">
              AI digest
            </span>
          </div>

          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="text-[11px] text-[#475569] tabular-nums">
                {formatRelativeTime(lastUpdated)}
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing || isLoading}
              className="p-2 rounded-lg text-[#475569] hover:text-[#94a3b8] hover:bg-[#1e293b] disabled:opacity-30 transition-all min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Refresh digest"
            >
              {isRefreshing ? (
                <Spinner className="h-[15px] w-[15px] text-[#6366f1]" />
              ) : (
                <RefreshIcon />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Filter chips */}
      {domains.length > 0 && (
        <div className="sticky top-[52px] z-10 bg-[#0f172a] border-b border-[#1e293b]">
          <DomainFilterChips
            domains={domains}
            active={activeDomain}
            onSelect={setActiveDomain}
          />
        </div>
      )}

      {/* Content */}
      <main className="max-w-[680px] mx-auto px-4 py-6">
        {error && (
          <div
            role="alert"
            className="mb-5 text-[13px] text-red-400 bg-red-950/50 border border-red-900/50 rounded-xl px-4 py-3"
          >
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner className="h-5 w-5 text-[#334155]" />
          </div>
        ) : Object.keys(grouped).length === 0 ? (
          <EmptyState
            title="No digest yet"
            subtitle="Hit the refresh button to fetch the latest AI developments."
          />
        ) : (
          <div className="space-y-8">
            {Object.entries(grouped).map(([domain, domainItems]) => (
              <DigestSection key={domain} domain={domain} items={domainItems} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
