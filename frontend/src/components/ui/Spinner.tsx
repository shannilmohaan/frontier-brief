interface SpinnerProps {
  className?: string;
}

export function Spinner({ className = "h-4 w-4" }: SpinnerProps) {
  return (
    <svg
      className={`animate-spin ${className}`}
      fill="none"
      viewBox="0 0 24 24"
      role="status"
      aria-label="Loading"
    >
      <circle
        className="opacity-20"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="3"
      />
      <path
        className="opacity-80"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}
