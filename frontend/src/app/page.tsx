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
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M13.5 2.5A6.5 6.5 0 1 1 8 1.5M13.5 2.5V6M13.5 2.5H10"
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
      setError("Could not load digest. Check your connection and try again.");
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
      const deadline = Date.now() + 30_000;
      while (Date.now() < deadline) {
        if (!mountedRef.current) return;
        await new Promise((r) => setTimeout(r, 3_000));
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
        setError("Refresh is taking longer than expected — it may still complete in the background.");
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
    <div className="min-h-screen bg-[#F8F9FA]">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-white/90 backdrop-blur-md border-b border-[#E8EAED]">
        <div className="max-w-[680px] mx-auto px-4 h-[52px] flex items-center justify-between">
          <h1 className="text-[17px] font-bold tracking-tight text-[#0F172A]">
            Frontier Brief
          </h1>
          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="text-xs text-[#94A3B8] hidden sm:block tabular-nums">
                {formatRelativeTime(lastUpdated)}
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing || isLoading}
              className="p-2 rounded-full text-[#475569] hover:bg-[#F1F5F9] disabled:opacity-40 transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Refresh digest"
            >
              {isRefreshing ? (
                <Spinner className="h-4 w-4" />
              ) : (
                <RefreshIcon />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Filter chips */}
      {domains.length > 0 && (
        <div className="sticky top-[52px] z-10 bg-[#F8F9FA] border-b border-[#E8EAED]">
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
            className="mb-5 text-sm text-red-700 bg-red-50 border border-red-100 rounded-xl px-4 py-3"
          >
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner className="h-5 w-5 text-[#94A3B8]" />
          </div>
        ) : Object.keys(grouped).length === 0 ? (
          <EmptyState
            title="No digest yet"
            subtitle="Trigger a refresh to fetch the latest AI developments."
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
