interface EmptyStateProps {
  title?: string;
  subtitle?: string;
}

export function EmptyState({
  title = "Nothing here yet",
  subtitle,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <p className="text-[15px] font-medium text-[#0F172A]">{title}</p>
      {subtitle && (
        <p className="mt-1.5 text-sm text-[#94A3B8] max-w-[260px]">{subtitle}</p>
      )}
    </div>
  );
}
