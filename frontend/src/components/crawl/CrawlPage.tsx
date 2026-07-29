import { useState, useRef } from 'react';
import { Radar } from 'lucide-react';
import { crawlService } from '@/services/crawlService';
import type { CrawlRequest, CrawlResponse } from '@/services/crawlService';
import { CrawlForm } from '@/components/crawl/CrawlForm';
import { CrawlProgress } from '@/components/crawl/CrawlProgress';
import { CrawlResults } from '@/components/crawl/CrawlResults';
import { EmptyState } from '@/components/shared/EmptyState';

export function CrawlPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<CrawlResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startTimer = () => {
    setElapsed(0);
    timerRef.current = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleCrawl = async (request: CrawlRequest) => {
    setIsRunning(true);
    setError(null);
    setResults(null);
    startTimer();

    try {
      const response = await crawlService.triggerCrawl(request);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Crawl failed');
    } finally {
      setIsRunning(false);
      stopTimer();
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="pb-2 border-b border-[var(--border-color)]">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
          Site Crawl & Test Generation
        </h1>
        <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
          Point at any URL — the agent will navigate the site, discover pages and elements, and auto-generate Playwright tests.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-[var(--color-dark-red-light)] border border-[var(--color-dark-red)] rounded text-xs text-[var(--color-dark-red)] font-mono" role="alert">
          {error}
        </div>
      )}

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: form */}
        <div className="lg:col-span-1">
          <CrawlForm onSubmit={handleCrawl} isRunning={isRunning} />
        </div>

        {/* Right: progress or results */}
        <div className="lg:col-span-2">
          {isRunning && (
            <CrawlProgress isRunning={isRunning} elapsedSeconds={elapsed} />
          )}

          {results && !isRunning && (
            <CrawlResults results={results} />
          )}

          {!results && !isRunning && (
            <EmptyState
              icon={<Radar className="w-6 h-6 text-[var(--text-muted)]" />}
              title="No crawl results yet"
              description="Enter a URL and click Start Crawl to discover pages and generate tests automatically."
            />
          )}
        </div>
      </div>
    </div>
  );
}
