import { Loader2, Globe } from 'lucide-react';

interface CrawlProgressProps {
  isRunning: boolean;
  elapsedSeconds: number;
}

export function CrawlProgress({ isRunning, elapsedSeconds }: CrawlProgressProps) {
  if (!isRunning) return null;

  return (
    <div className="app-card p-5 space-y-3">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-full badge-orange">
          <Loader2 className="w-5 h-5 animate-spin" />
        </div>
        <div>
          <h4 className="font-bold text-sm text-[var(--text-primary)]">Crawl in Progress</h4>
          <p className="text-xs text-[var(--text-muted)] font-mono">
            Discovering pages and extracting elements...
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs font-mono text-[var(--text-secondary)]">
        <span className="flex items-center gap-1">
          <Globe className="w-3.5 h-3.5 text-[var(--color-matcha)]" />
          Navigating site
        </span>
        <span>
          Elapsed: {Math.floor(elapsedSeconds / 60)}m {Math.floor(elapsedSeconds % 60)}s
        </span>
      </div>

      <div className="w-full h-1.5 bg-[var(--bg-card-alt)] rounded-full overflow-hidden">
        <div className="h-full bg-[var(--color-matcha)] rounded-full animate-pulse" style={{ width: '60%' }} />
      </div>
    </div>
  );
}
