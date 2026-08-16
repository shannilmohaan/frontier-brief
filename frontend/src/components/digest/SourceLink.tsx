interface SourceLinkProps {
  href: string;
  children: React.ReactNode;
}

export function SourceLink({ href, children }: SourceLinkProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1.5 text-[12px] font-medium text-[#6366f1] hover:text-[#818cf8] transition-colors min-h-[44px] -my-2 py-2"
    >
      <span>{children}</span>
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
        <path d="M1 9L9 1M9 1H3M9 1V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </a>
  );
}
