"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { DomainFilterChips } from "@/components/filters/DomainFilterChips";
import { DigestSection } from "@/components/digest/DigestSection";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { fetchLatestDigest, fetchHistory, pollRefreshStatus, triggerRefresh } from "@/lib/api";
import type { CycleInfo, DigestItem, Domain } from "@/lib/types";

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function RefreshIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
      <path d="M12.5 2.5A6 6 0 1 1 7.5 1.5M12.5 2.5V5.5M12.5 2.5H9.5"
        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
      <circle cx="7.5" cy="7.5" r="6" stroke="currentColor" strokeWidth="1.5" />
      <path d="M7.5 4.5V7.5L9.5 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function BackIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M9 2L4 7L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
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
  const [activeCycleId, setActiveCycleId] = useState<string | null>(null);

  // History state
  const [showHistory, setShowHistory] = useState(false);
  const [cycles, setCycles] = useState<CycleInfo[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const loadDigest = useCallback(async (cycleId?: string) => {
    setIsLoading(true);
    try {
      const data = await fetchLatestDigest(undefined, cycleId);
      if (!mountedRef.current) return;
      setItems(data.items);
      setActiveCycleId(data.cycle_id);
      if (data.items.length > 0) {
        const latest = data.items.reduce((a, b) => a.created_at > b.created_at ? a : b);
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

  useEffect(() => { loadDigest(); }, [loadDigest]);

  const openHistory = async () => {
    setShowHistory(true);
    setHistoryLoading(true);
    try {
      const data = await fetchHistory();
      if (mountedRef.current) setCycles(data.cycles);
    } catch {
      // silently fail — list stays empty
    } finally {
      if (mountedRef.current) setHistoryLoading(false);
    }
  };

  const selectCycle = async (cycleId: string) => {
    setShowHistory(false);
    setActiveDomain(null);
    await loadDigest(cycleId);
  };

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
          setActiveDomain(null);
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

  const grouped = filteredItems.reduce<Record<string, DigestItem[]>>((acc, item) => {
    const domain = item.domain_tags[0] ?? "AI Research";
    acc[domain] = [...(acc[domain] ?? []), item];
    return acc;
  }, {});

  const isViewingPast = activeCycleId !== null && cycles.length > 0 &&
    cycles[0]?.id !== activeCycleId;

  return (
    <div className="min-h-screen bg-[#0f172a]">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-[#0a0f1e]/95 backdrop-blur-md border-b border-[#1e293b]">
        <div className="max-w-[680px] mx-auto px-4 h-[52px] flex items-center justify-between">
          <button
            onClick={() => { setShowHistory(false); if (isViewingPast) loadDigest(); }}
            className="flex items-center gap-2"
          >
            <span className="text-[16px] font-bold tracking-tight text-[#f1f5f9]">
              Frontier Brief
            </span>
            {isViewingPast && (
              <span className="text-[11px] text-[#6366f1] font-medium">past digest</span>
            )}
          </button>

          <div className="flex items-center gap-1">
            {lastUpdated && !showHistory && (
              <span className="text-[11px] text-[#475569] tabular-nums mr-1">
                {formatRelativeTime(lastUpdated)}
              </span>
            )}
            <button
              onClick={() => showHistory ? setShowHistory(false) : openHistory()}
              className={[
                "p-2 rounded-lg transition-all min-w-[44px] min-h-[44px] flex items-center justify-center",
                showHistory
                  ? "text-[#6366f1] bg-[#1e293b]"
                  : "text-[#475569] hover:text-[#94a3b8] hover:bg-[#1e293b]",
              ].join(" ")}
              aria-label="Digest history"
            >
              {showHistory ? <BackIcon /> : <HistoryIcon />}
            </button>
            {!showHistory && (
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
            )}
          </div>
        </div>
      </header>

      {/* Filter chips — only in digest view */}
      {!showHistory && domains.length > 0 && (
        <div className="sticky top-[52px] z-10 bg-[#0f172a] border-b border-[#1e293b]">
          <DomainFilterChips domains={domains} active={activeDomain} onSelect={setActiveDomain} />
        </div>
      )}

      {/* Main content */}
      <main className="max-w-[680px] mx-auto px-4 py-6">
        {error && (
          <div role="alert" className="mb-5 text-[13px] text-red-400 bg-red-950/50 border border-red-900/50 rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {showHistory ? (
          /* History list */
          <div>
            <p className="text-[11px] font-semibold tracking-[0.12em] uppercase text-[#475569] mb-4">
              Past Digests
            </p>
            {historyLoading ? (
              <div className="flex justify-center py-16">
                <Spinner className="h-5 w-5 text-[#334155]" />
              </div>
            ) : cycles.length === 0 ? (
              <EmptyState title="No history yet" subtitle="Run a refresh to create your first digest." />
            ) : (
              <div className="flex flex-col gap-2">
                {cycles.map((cycle, i) => (
                  <button
                    key={cycle.id}
                    onClick={() => selectCycle(cycle.id)}
                    className="flex items-center justify-between w-full bg-[#1e293b] hover:bg-[#263347] border border-[#334155] hover:border-[#475569] rounded-xl px-4 py-3.5 transition-all text-left min-h-[56px]"
                  >
                    <div className="flex items-center gap-3">
                      {i === 0 && (
                        <span className="text-[10px] font-semibold text-[#6366f1] bg-[#1e1b4b] px-2 py-0.5 rounded-full">
                          Latest
                        </span>
                      )}
                      <span className="text-[14px] text-[#e2e8f0] font-medium">
                        {formatDate(cycle.completed_at)}
                      </span>
                    </div>
                    <span className="text-[12px] text-[#475569] shrink-0 ml-2">
                      {cycle.items_synthesized} items
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner className="h-5 w-5 text-[#334155]" />
          </div>
        ) : Object.keys(grouped).length === 0 ? (
          <EmptyState title="No digest yet" subtitle="Hit the refresh button to fetch the latest AI developments." />
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
