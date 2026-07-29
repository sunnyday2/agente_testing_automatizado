import { CheckCircle2, FileCode, Globe, Layers } from 'lucide-react';
import type { CrawlResponse } from '@/services/crawlService';

interface CrawlResultsProps {
  results: CrawlResponse;
}

export function CrawlResults({ results }: CrawlResultsProps) {
  return (
    <div className="space-y-4">
      {/* Summary stats */}
      <div className="app-card p-4">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-4 h-4 text-[var(--color-matcha)]" />
          <h4 className="font-bold text-sm text-[var(--text-primary)]">Crawl Complete</h4>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-[var(--bg-card-alt)] rounded text-center">
            <p className="text-lg font-bold font-mono text-[var(--text-primary)]">{results.pages_discovered}</p>
            <p className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Pages</p>
          </div>
          <div className="p-3 bg-[var(--bg-card-alt)] rounded text-center">
            <p className="text-lg font-bold font-mono text-[var(--text-primary)]">{results.elements_found}</p>
            <p className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Elements</p>
          </div>
          <div className="p-3 bg-[var(--bg-card-alt)] rounded text-center">
            <p className="text-lg font-bold font-mono text-[var(--color-matcha)]">{results.tests_generated}</p>
            <p className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Tests Generated</p>
          </div>
          <div className="p-3 bg-[var(--bg-card-alt)] rounded text-center">
            <p className="text-lg font-bold font-mono text-[var(--text-primary)]">{results.generated_files.length}</p>
            <p className="text-[10px] font-mono text-[var(--text-muted)] uppercase">Files</p>
          </div>
        </div>
      </div>

      {/* Site map */}
      {results.site_map.length > 0 && (
        <div className="app-card overflow-hidden">
          <div className="p-3 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center gap-2">
            <Globe className="w-4 h-4 text-[var(--color-okra)]" />
            <h4 className="font-bold text-xs font-mono uppercase text-[var(--text-primary)]">
              Discovered Pages ({results.site_map.length})
            </h4>
          </div>
          <div className="divide-y divide-[var(--border-color)] max-h-64 overflow-y-auto custom-scrollbar">
            {results.site_map.map((page, i) => (
              <div key={i} className="px-4 py-2.5 flex items-center justify-between text-xs font-mono">
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-[var(--text-primary)] truncate">{page.title || page.url}</p>
                  <p className="text-[var(--text-muted)] truncate">{page.url}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0 text-[var(--text-muted)]">
                  <span>{page.elements_count} elements</span>
                  <span>{page.links_count} links</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated files */}
      {results.generated_files.length > 0 && (
        <div className="app-card overflow-hidden">
          <div className="p-3 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center gap-2">
            <FileCode className="w-4 h-4 text-[var(--color-matcha)]" />
            <h4 className="font-bold text-xs font-mono uppercase text-[var(--text-primary)]">
              Generated Files ({results.generated_files.length})
            </h4>
          </div>
          <div className="divide-y divide-[var(--border-color)] max-h-48 overflow-y-auto custom-scrollbar">
            {results.generated_files.map((file, i) => (
              <div key={i} className="px-4 py-2 flex items-center gap-2 text-xs font-mono">
                <Layers className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0" />
                <span className="text-[var(--text-primary)] truncate">{file}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
