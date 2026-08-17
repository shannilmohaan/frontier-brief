"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { DomainFilterChips } from "@/components/filters/DomainFilterChips";
import { DigestSection } from "@/components/digest/DigestSection";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { fetchLatestDigest, fetchHistory, pollRefreshStatus, triggerRefresh } from "@/lib/api";
import type { CycleInfo, DigestItem, Domain } from "@/lib/types";

function formatCycleDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
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

function ChevronLeft() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M9 2L4 7L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M5 2L10 7L5 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Home() {
  const [items, setItems] = useState<DigestItem[]>([]);
  const [activeDomain, setActiveDomain] = useState<Domain | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cycle navigation
  const [cycles, setCycles] = useState<CycleInfo[]>([]);
  const [currentCycleIndex, setCurrentCycleIndex] = useState(0);

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
      setError(null);
    } catch {
      if (!mountedRef.current) return;
      setError("Could not load digest.");
    } finally {
      if (mountedRef.current) setIsLoading(false);
    }
  }, []);

  // On mount: load history list, then load the latest digest
  useEffect(() => {
    (async () => {
      try {
        const data = await fetchHistory();
        if (!mountedRef.current) return;
        setCycles(data.cycles);
        setCurrentCycleIndex(0);
        if (data.cycles.length > 0) {
          await loadDigest(data.cycles[0].id);
        } else {
          await loadDigest();
        }
      } catch {
        if (mountedRef.current) await loadDigest();
      }
    })();
  }, [loadDigest]);

  const goToIndex = useCallback(async (index: number) => {
    if (index < 0 || index >= cycles.length) return;
    setCurrentCycleIndex(index);
    setActiveDomain(null);
    await loadDigest(cycles[index].id);
  }, [cycles, loadDigest]);

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
          // Reload history and show the new cycle
          const data = await fetchHistory();
          if (!mountedRef.current) return;
          setCycles(data.cycles);
          setCurrentCycleIndex(0);
          setActiveDomain(null);
          await loadDigest(data.cycles[0]?.id);
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
    const domain = item.domain_tags[0] ?? "AI";
    acc[domain] = [...(acc[domain] ?? []), item];
    return acc;
  }, {});

  const currentCycle = cycles[currentCycleIndex] ?? null;
  const canGoOlder = currentCycleIndex < cycles.length - 1;
  const canGoNewer = currentCycleIndex > 0;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-[#e2e8f0]">
        <div className="max-w-[680px] mx-auto px-4 h-[52px] flex items-center justify-between">
          <button
            onClick={() => { setActiveDomain(null); setCurrentCycleIndex(0); if (cycles[0]) loadDigest(cycles[0].id); }}
            className="text-[16px] font-bold tracking-tight text-[#0f172a]"
          >
            Frontier Brief
          </button>

          <div className="flex items-center gap-1">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing || isLoading}
              className="p-2 rounded-lg text-[#94a3b8] hover:text-[#64748b] hover:bg-[#f1f5f9] disabled:opacity-30 transition-all min-w-[44px] min-h-[44px] flex items-center justify-center"
              aria-label="Refresh digest"
            >
              {isRefreshing ? (
                <Spinner className="h-[15px] w-[15px] text-[#4f46e5]" />
              ) : (
                <RefreshIcon />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Domain filter chips */}
      {domains.length > 0 && (
        <div className="sticky top-[52px] z-10 bg-white border-b border-[#e2e8f0]">
          <DomainFilterChips domains={domains} active={activeDomain} onSelect={setActiveDomain} />
        </div>
      )}

      {/* Main content */}
      <main className="max-w-[680px] mx-auto px-4 py-6">
        {error && (
          <div role="alert" className="mb-5 text-[13px] text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-24">
            <Spinner className="h-5 w-5 text-[#d1d5db]" />
          </div>
        ) : Object.keys(grouped).length === 0 ? (
          <EmptyState
            title="No digest yet"
            subtitle="Hit the refresh button to fetch the latest AI developments."
          />
        ) : (
          <>
            {/* Cycle navigation */}
            {cycles.length > 1 && (
              <div className="flex items-center justify-between mb-6 py-2">
                <button
                  onClick={() => goToIndex(currentCycleIndex + 1)}
                  disabled={!canGoOlder}
                  className="flex items-center gap-1.5 text-[12px] font-medium text-[#64748b] hover:text-[#0f172a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors min-h-[44px] px-2"
                  aria-label="Older digest"
                >
                  <ChevronLeft />
                  Older
                </button>

                <div className="text-center">
                  {currentCycle && (
                    <p className="text-[12px] text-[#94a3b8]">
                      {formatCycleDate(currentCycle.completed_at)}
                      <span className="mx-1.5">·</span>
                      {currentCycle.items_synthesized} items
                    </p>
                  )}
                  {currentCycleIndex === 0 && (
                    <span className="text-[10px] font-semibold text-[#4f46e5] uppercase tracking-wider">
                      Latest
                    </span>
                  )}
                </div>

                <button
                  onClick={() => goToIndex(currentCycleIndex - 1)}
                  disabled={!canGoNewer}
                  className="flex items-center gap-1.5 text-[12px] font-medium text-[#64748b] hover:text-[#0f172a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors min-h-[44px] px-2"
                  aria-label="Newer digest"
                >
                  Newer
                  <ChevronRight />
                </button>
              </div>
            )}

            {/* Digest content */}
            <div className="space-y-8">
              {Object.entries(grouped).map(([domain, domainItems]) => (
                <DigestSection key={domain} domain={domain} items={domainItems} />
              ))}
            </div>

            {/* Bottom navigation (duplicate for convenience) */}
            {cycles.length > 1 && (
              <div className="flex items-center justify-between mt-10 pt-6 border-t border-[#f1f5f9]">
                <button
                  onClick={() => goToIndex(currentCycleIndex + 1)}
                  disabled={!canGoOlder}
                  className="flex items-center gap-1.5 text-[12px] font-medium text-[#64748b] hover:text-[#0f172a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors min-h-[44px] px-2"
                >
                  <ChevronLeft />
                  Older
                </button>
                <button
                  onClick={() => goToIndex(currentCycleIndex - 1)}
                  disabled={!canGoNewer}
                  className="flex items-center gap-1.5 text-[12px] font-medium text-[#64748b] hover:text-[#0f172a] disabled:opacity-30 disabled:cursor-not-allowed transition-colors min-h-[44px] px-2"
                >
                  Newer
                  <ChevronRight />
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
