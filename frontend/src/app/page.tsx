"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { DomainFilterChips } from "@/components/filters/DomainFilterChips";
import { DigestSection } from "@/components/digest/DigestSection";
import { HeroCard } from "@/components/digest/HeroCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkeletonSection } from "@/components/ui/SkeletonCard";
import { fetchLatestDigest, fetchHistory, pollRefreshStatus, triggerRefresh } from "@/lib/api";
import type { CycleInfo, DigestItem, Domain } from "@/lib/types";

// Task-oriented tabs — each maps to a domain or a content filter
// Per spec §8 and the homepage section order from spec §21
type NavTab = "today" | "build" | "agents" | "architecture" | "ai-coding" | "production" | "tools" | "learn";

const NAV_TABS: { id: NavTab; label: string; domain?: Domain; contentFilter?: (i: DigestItem) => boolean }[] = [
  { id: "today",        label: "Today" },
  { id: "build",        label: "Build",        domain: "AI Applications" },
  { id: "agents",       label: "Agents",       domain: "Agentic AI" },
  { id: "architecture", label: "Architecture", domain: "AI Architecture" },
  { id: "ai-coding",    label: "AI Coding",    domain: "AI Coding" },
  { id: "production",   label: "Production",   domain: "Production AI" },
  { id: "tools",        label: "Tools",        domain: "AI Engineering" },
  { id: "learn",        label: "Learn",        contentFilter: (i) => i.content_type === "video" || i.content_type === "podcast" || i.content_type === "newsletter" },
];

// Homepage section order per spec §21
const SECTION_ORDER: Domain[] = [
  "AI Coding",
  "Agentic AI",
  "AI Architecture",
  "Production AI",
  "AI Engineering",
  "Models",
  "AI Applications",
  "Industry",
];

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    weekday: "short", month: "long", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function RefreshIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 15 15" fill="none" aria-hidden="true">
      <path d="M12.5 2.5A6 6 0 1 1 7.5 1.5M12.5 2.5V5.5M12.5 2.5H9.5"
        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ChevronLeft() {
  return (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M9 2L4 7L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M5 2L10 7L5 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Spinner({ className = "" }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
      <path className="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

export default function Home() {
  const [items, setItems] = useState<DigestItem[]>([]);
  const [activeTab, setActiveTab] = useState<NavTab>("today");
  const [activeDomain, setActiveDomain] = useState<Domain | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
      setError("Could not load digest. Check your connection and try again.");
    } finally {
      if (mountedRef.current) setIsLoading(false);
    }
  }, []);

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
    setActiveTab("today");
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
          const data = await fetchHistory();
          if (!mountedRef.current) return;
          setCycles(data.cycles);
          setCurrentCycleIndex(0);
          setActiveDomain(null);
          setActiveTab("today");
          await loadDigest(data.cycles[0]?.id);
          break;
        }
        if (status === "failed") {
          finished = true;
          if (mountedRef.current) setError("Refresh failed. Please try again.");
          break;
        }
      }
      if (!finished && mountedRef.current) setError("Still processing — check back in a minute.");
    } catch {
      if (mountedRef.current) setError("Refresh failed. Please try again.");
    } finally {
      if (mountedRef.current) setIsRefreshing(false);
    }
  };

  // Apply tab filter
  const currentTabDef = NAV_TABS.find((t) => t.id === activeTab)!;
  const tabFiltered = (() => {
    if (currentTabDef.domain) return items.filter((i) => i.domain_tags.includes(currentTabDef.domain!));
    if (currentTabDef.contentFilter) return items.filter(currentTabDef.contentFilter);
    return items; // "today" = all
  })();

  // Apply secondary domain chip filter
  const domainFiltered = activeDomain
    ? tabFiltered.filter((i) => i.domain_tags.includes(activeDomain))
    : tabFiltered;

  // Available domains for chip strip (from currently visible items)
  const domains = Array.from(
    new Set(tabFiltered.flatMap((i) => i.domain_tags).filter(Boolean) as Domain[])
  );

  // Hero = highest relevance_score item in filtered set
  const heroItem = domainFiltered[0] ?? null;
  const remainingItems = domainFiltered.slice(1);

  // Group remaining items by domain, then sort groups by SECTION_ORDER
  const grouped = remainingItems.reduce<Record<string, DigestItem[]>>((acc, item) => {
    const domain = item.domain_tags[0] ?? "Industry";
    acc[domain] = [...(acc[domain] ?? []), item];
    return acc;
  }, {});

  const sortedSections = [
    ...SECTION_ORDER.filter((d) => grouped[d]),
    ...Object.keys(grouped).filter((d) => !SECTION_ORDER.includes(d as Domain)),
  ];

  const currentCycle = cycles[currentCycleIndex] ?? null;
  const canGoOlder = currentCycleIndex < cycles.length - 1;
  const canGoNewer = currentCycleIndex > 0;
  const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>

      {/* Header */}
      <header
        className="sticky top-0 z-20 backdrop-blur-md"
        style={{ background: "rgba(8,9,14,0.90)", borderBottom: "1px solid var(--border)" }}
      >
        <div className="max-w-[960px] mx-auto px-4">
          {/* Top bar */}
          <div className="h-[52px] flex items-center justify-between">
            <button
              onClick={() => {
                setActiveDomain(null);
                setActiveTab("today");
                setCurrentCycleIndex(0);
                if (cycles[0]) loadDigest(cycles[0].id);
              }}
              className="flex items-center gap-2"
            >
              <span
                className="text-[13px] font-bold tracking-[0.15em] uppercase"
                style={{ color: "var(--text-primary)" }}
              >
                Frontier Brief
              </span>
              <span
                className="text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase tracking-widest"
                style={{ background: "var(--surface-raised)", color: "var(--text-muted)" }}
              >
                AI Builder
              </span>
            </button>

            <div className="flex items-center gap-3">
              {currentCycle && (
                <span className="hidden sm:block text-[11px]" style={{ color: "var(--text-muted)" }}>
                  {formatDate(currentCycle.completed_at)}
                </span>
              )}
              <button
                onClick={handleRefresh}
                disabled={isRefreshing || isLoading}
                className="flex items-center gap-1.5 text-[11px] font-medium px-3 py-2 rounded-lg transition-all disabled:opacity-30 min-h-[36px]"
                style={{ color: "var(--text-secondary)", border: "1px solid var(--border)", background: "var(--surface)" }}
                aria-label="Refresh digest"
              >
                {isRefreshing ? (
                  <Spinner className="h-3 w-3 text-[#5b8af0]" />
                ) : (
                  <RefreshIcon />
                )}
                <span className="hidden sm:inline">{isRefreshing ? "Refreshing…" : "Refresh"}</span>
              </button>
            </div>
          </div>

          {/* Nav tabs — task-oriented per spec §8 */}
          <div className="flex gap-0 overflow-x-auto hide-scrollbar border-t" style={{ borderColor: "var(--border-muted)" }}>
            {NAV_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setActiveDomain(null); }}
                className="shrink-0 px-3 sm:px-4 py-2.5 text-[12px] font-medium transition-all whitespace-nowrap border-b-2"
                style={
                  activeTab === tab.id
                    ? { color: "var(--text-primary)", borderColor: "var(--accent)" }
                    : { color: "var(--text-muted)", borderColor: "transparent" }
                }
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Domain filter chips — only show when on Today tab with multiple domains */}
      {!isLoading && activeTab === "today" && domains.length > 1 && (
        <div
          className="sticky z-10"
          style={{
            top: "96px",
            background: "rgba(8,9,14,0.92)",
            backdropFilter: "blur(8px)",
            borderBottom: "1px solid var(--border-muted)",
          }}
        >
          <div className="max-w-[960px] mx-auto">
            <DomainFilterChips domains={domains} active={activeDomain} onSelect={setActiveDomain} />
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="max-w-[960px] mx-auto px-4 py-6">

        {/* Error banner */}
        {error && (
          <div
            role="alert"
            className="mb-5 text-[13px] rounded-lg px-4 py-3"
            style={{ color: "#fca5a5", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.20)" }}
          >
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="space-y-10">
            <div
              className="rounded-xl p-6 animate-pulse"
              style={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }}
            >
              <div className="h-3 w-40 rounded mb-4" style={{ background: "var(--border)" }} />
              <div className="h-7 w-4/5 rounded mb-2" style={{ background: "var(--border)" }} />
              <div className="h-7 w-3/5 rounded mb-5" style={{ background: "var(--border)" }} />
              <div className="h-3 w-full rounded mb-2" style={{ background: "var(--border)" }} />
              <div className="h-3 w-11/12 rounded mb-2" style={{ background: "var(--border)" }} />
              <div className="h-3 w-4/5 rounded" style={{ background: "var(--border)" }} />
            </div>
            <SkeletonSection />
            <SkeletonSection />
          </div>
        ) : domainFiltered.length === 0 ? (
          <EmptyState
            title={activeTab === "today" ? "No digest yet" : `Nothing in ${currentTabDef.label} yet`}
            subtitle={
              activeTab === "today"
                ? "Trigger a refresh to fetch the latest AI developments."
                : `No ${currentTabDef.label.toLowerCase()} content found in this digest cycle.`
            }
            onRefresh={handleRefresh}
          />
        ) : (
          <>
            {/* Briefing header */}
            <div className="mb-6">
              <p className="text-[11px] font-semibold tracking-widest uppercase mb-1" style={{ color: "var(--text-muted)" }}>
                AI Builder Briefing
              </p>
              <h1
                className="text-[20px] sm:text-[26px] leading-tight"
                style={{ fontFamily: "var(--font-serif)", color: "var(--text-primary)" }}
              >
                {activeTab === "today"
                  ? "What matters for AI builders today."
                  : `${currentTabDef.label} — what changed this week.`}
              </h1>
              <p className="text-[12px] mt-1" style={{ color: "var(--text-muted)" }}>
                {today}
                {currentCycle && <span> · {currentCycle.items_synthesized} curated items</span>}
              </p>
            </div>

            {/* Cycle navigation */}
            {cycles.length > 1 && (
              <div
                className="flex items-center justify-between mb-6 px-3 py-2 rounded-lg"
                style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
              >
                <button
                  onClick={() => goToIndex(currentCycleIndex + 1)}
                  disabled={!canGoOlder}
                  className="flex items-center gap-1 text-[11px] font-medium transition-colors disabled:opacity-25 min-h-[36px] px-2"
                  style={{ color: "var(--text-secondary)" }}
                  aria-label="Older digest"
                >
                  <ChevronLeft /> Older
                </button>
                <div className="text-center">
                  {currentCycleIndex === 0 && (
                    <span className="text-[9px] font-bold tracking-widest uppercase mr-2" style={{ color: "var(--accent)" }}>
                      Latest
                    </span>
                  )}
                  {currentCycle && (
                    <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                      {formatDate(currentCycle.completed_at)}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => goToIndex(currentCycleIndex - 1)}
                  disabled={!canGoNewer}
                  className="flex items-center gap-1 text-[11px] font-medium transition-colors disabled:opacity-25 min-h-[36px] px-2"
                  style={{ color: "var(--text-secondary)" }}
                  aria-label="Newer digest"
                >
                  Newer <ChevronRight />
                </button>
              </div>
            )}

            {/* Hero card — top story */}
            {heroItem && <HeroCard item={heroItem} />}

            {/* Domain sections — remaining items, ordered per spec §21 */}
            {sortedSections.length > 0 && (
              <div className="space-y-8">
                {sortedSections.map((domain) => (
                  <DigestSection key={domain} domain={domain} items={grouped[domain]} />
                ))}
              </div>
            )}

            {/* Bottom nav */}
            {cycles.length > 1 && (
              <div
                className="flex items-center justify-between mt-12 pt-5"
                style={{ borderTop: "1px solid var(--border)" }}
              >
                <button
                  onClick={() => goToIndex(currentCycleIndex + 1)}
                  disabled={!canGoOlder}
                  className="flex items-center gap-1 text-[11px] font-medium disabled:opacity-25 min-h-[44px] px-2"
                  style={{ color: "var(--text-secondary)" }}
                >
                  <ChevronLeft /> Older
                </button>
                <button
                  onClick={() => goToIndex(currentCycleIndex - 1)}
                  disabled={!canGoNewer}
                  className="flex items-center gap-1 text-[11px] font-medium disabled:opacity-25 min-h-[44px] px-2"
                  style={{ color: "var(--text-secondary)" }}
                >
                  Newer <ChevronRight />
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
