export function SkeletonCard() {
  return (
    <div className="py-5 border-b" style={{ borderColor: "var(--border-muted)" }}>
      <div className="flex gap-3">
        <div className="flex-1 space-y-2.5">
          <div className="h-2 w-14 rounded animate-pulse" style={{ background: "var(--surface-raised)" }} />
          <div className="h-3.5 w-4/5 rounded animate-pulse" style={{ background: "var(--surface-raised)" }} />
          <div className="h-3 w-full rounded animate-pulse" style={{ background: "var(--surface-raised)" }} />
          <div className="h-3 w-11/12 rounded animate-pulse" style={{ background: "var(--surface-raised)" }} />
          <div className="h-3 w-2/3 rounded animate-pulse" style={{ background: "var(--surface-raised)" }} />
          <div className="h-2.5 w-28 rounded animate-pulse mt-1" style={{ background: "var(--surface-raised)" }} />
        </div>
        <div className="shrink-0 w-24 h-16 rounded-lg animate-pulse" style={{ background: "var(--surface-raised)" }} />
      </div>
    </div>
  );
}

export function SkeletonSection() {
  return (
    <div>
      <div className="h-3 w-32 rounded animate-pulse mb-4" style={{ background: "var(--surface-raised)" }} />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </div>
  );
}
