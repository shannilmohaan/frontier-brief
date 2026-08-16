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
      <p className="text-[15px] font-medium text-[#f1f5f9]">{title}</p>
      {subtitle && (
        <p className="mt-1.5 text-sm text-[#475569] max-w-[260px]">{subtitle}</p>
      )}
    </div>
  );
}
