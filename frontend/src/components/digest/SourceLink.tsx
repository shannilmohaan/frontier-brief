interface SourceLinkProps {
  href: string;
  children: React.ReactNode;
}

function isSafeUrl(url: string): boolean {
  try {
    const { protocol } = new URL(url);
    return protocol === "https:" || protocol === "http:";
  } catch {
    return false;
  }
}

export function SourceLink({ href, children }: SourceLinkProps) {
  if (!isSafeUrl(href)) {
    return <span className="text-sm font-medium text-[#94A3B8]">{children}</span>;
  }

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-sm font-medium text-[#0F172A] hover:underline underline-offset-2 min-h-[44px] py-2"
    >
      {children}
      <svg
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
        aria-hidden="true"
        className="opacity-40 shrink-0"
      >
        <path
          d="M2.5 9.5L9.5 2.5M9.5 2.5H5M9.5 2.5V7"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </a>
  );
}
