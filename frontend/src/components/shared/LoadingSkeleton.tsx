interface LoadingSkeletonProps {
  /** Number of skeleton rows to render */
  lines?: number;
  /** Additional CSS classes */
  className?: string;
}

export function LoadingSkeleton({ lines = 3, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`animate-pulse space-y-3 ${className}`} aria-label="Loading content">
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className="h-4 bg-[var(--bg-card-alt)] rounded"
          style={{ width: `${85 - i * 10}%` }}
        />
      ))}
    </div>
  );
}
