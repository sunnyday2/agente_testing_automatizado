import { useState } from 'react';
import { Globe, Play, Settings } from 'lucide-react';
import type { CrawlRequest } from '@/services/crawlService';

interface CrawlFormProps {
  onSubmit: (request: CrawlRequest) => Promise<void>;
  isRunning: boolean;
}

export function CrawlForm({ onSubmit, isRunning }: CrawlFormProps) {
  const [url, setUrl] = useState('');
  const [maxDepth, setMaxDepth] = useState(3);
  const [maxPages, setMaxPages] = useState(30);
  const [generateTests, setGenerateTests] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || isRunning) return;

    await onSubmit({
      url: url.trim(),
      max_depth: maxDepth,
      max_pages: maxPages,
      generate_tests: generateTests,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="app-card p-5 space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-[var(--border-color)]">
        <Globe className="w-4 h-4 text-[var(--color-matcha)]" />
        <h3 className="font-bold text-sm text-[var(--text-primary)]">Crawl Configuration</h3>
      </div>

      {/* URL input */}
      <div>
        <label htmlFor="crawl-url" className="block text-xs font-mono font-bold uppercase mb-1">
          Target URL <span className="text-[var(--color-dark-red)]">*</span>
        </label>
        <input
          id="crawl-url"
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://your-app.com"
          className="w-full px-3 py-2.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
        />
        <p className="text-[10px] text-[var(--text-muted)] font-mono mt-1">
          The crawler will navigate this site using Playwright and discover all pages and elements.
        </p>
      </div>

      {/* Generate tests toggle */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="generate-tests"
          checked={generateTests}
          onChange={(e) => setGenerateTests(e.target.checked)}
          className="w-4 h-4 rounded border-[var(--border-color)] accent-[var(--color-matcha)] cursor-pointer"
        />
        <label htmlFor="generate-tests" className="text-xs font-medium cursor-pointer text-[var(--text-primary)]">
          Auto-generate POM classes and test scripts from discovered pages
        </label>
      </div>

      {/* Advanced toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-1.5 text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
      >
        <Settings className="w-3.5 h-3.5" />
        <span>{showAdvanced ? 'Hide' : 'Show'} advanced options</span>
      </button>

      {showAdvanced && (
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[var(--border-subtle)]">
          <div>
            <label htmlFor="max-depth" className="block text-xs font-mono font-bold uppercase mb-1">
              Max Depth
            </label>
            <input
              id="max-depth"
              type="number"
              min={1}
              max={10}
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
            <p className="text-[10px] text-[var(--text-muted)] mt-0.5">Navigation levels (1-10)</p>
          </div>
          <div>
            <label htmlFor="max-pages" className="block text-xs font-mono font-bold uppercase mb-1">
              Max Pages
            </label>
            <input
              id="max-pages"
              type="number"
              min={1}
              max={200}
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
            <p className="text-[10px] text-[var(--text-muted)] mt-0.5">Page visit limit (1-200)</p>
          </div>
        </div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={isRunning || !url.trim()}
        className="w-full py-2.5 btn-matcha text-xs font-mono font-bold flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Play className="w-4 h-4 fill-current" />
        <span>{isRunning ? 'Crawling...' : 'Start Crawl'}</span>
      </button>
    </form>
  );
}
