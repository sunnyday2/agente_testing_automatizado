import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { useTestSuites } from '@/hooks/useTestSuites';
import { 
  FlaskConical, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Terminal, 
  Search,
  Filter,
  RotateCw
} from 'lucide-react';

export const TestSuites: React.FC = () => {
  const { testSuites: contextSuites, runTestSuite: contextRunSuite } = useApp();
  const apiSuites = useTestSuites();

  // Use API data when available, fall back to context mock data
  const hasApiData = apiSuites.suites.length > 0 && !apiSuites.error;
  const testSuites = hasApiData ? apiSuites.suites : contextSuites;
  const runTestSuite = hasApiData
    ? (id: string) => { apiSuites.runSuite(id); }
    : contextRunSuite;

  const [selectedSuiteId, setSelectedSuiteId] = useState<string>(testSuites[0]?.id || '');
  const [filterCategory, setFilterCategory] = useState<string>('ALL');

  const categories = ['ALL', 'E2E Validation', 'API Security', 'Infrastructure', 'Performance'];

  const filteredSuites = testSuites.filter((suite) => {
    return filterCategory === 'ALL' || suite.category === filterCategory;
  });

  const activeSuite = testSuites.find((s) => s.id === selectedSuiteId) || testSuites[0];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-color)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            Test Automation Lab
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            Execute, inspect, and debug test suite assertion steps across isolated sandbox environments.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={async () => {
              const { testSuitesService } = await import('@/services/testSuitesService');
              await testSuitesService.scan();
              if (hasApiData) apiSuites.refresh();
            }}
            className="btn-outline px-4 py-2 text-xs font-mono font-bold flex items-center gap-2 shrink-0"
          >
            <Search className="w-4 h-4" />
            <span>Scan Tests</span>
          </button>
          <button
            onClick={() => {
              testSuites.forEach((s) => runTestSuite(s.id));
            }}
            className="btn-matcha px-4 py-2 text-xs font-mono font-bold flex items-center gap-2 shadow-sm shrink-0"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Execute All Active Suites</span>
          </button>
        </div>
      </div>

      {/* Category Filters */}
      <div className="flex items-center gap-2 overflow-x-auto custom-scrollbar pb-1">
        <span className="text-xs font-mono font-bold text-[var(--text-muted)] flex items-center gap-1 shrink-0">
          <Filter className="w-3.5 h-3.5" /> SUITE TYPE:
        </span>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`px-3 py-1 rounded-md text-xs font-mono font-medium shrink-0 transition-all ${
              filterCategory === cat
                ? 'bg-[var(--text-primary)] text-[var(--bg-card)] font-bold'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--text-secondary)]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid: Left Suites List, Right Console Step Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Suites Table List */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold text-[var(--text-primary)] font-mono uppercase">
            Registered Suites ({filteredSuites.length})
          </h2>

          <div className="space-y-2 max-h-[calc(100vh-280px)] overflow-y-auto custom-scrollbar pr-1">
            {filteredSuites.map((suite) => {
              const isSelected = suite.id === activeSuite?.id;
              return (
                <div
                  key={suite.id}
                  onClick={() => setSelectedSuiteId(suite.id)}
                  className={`app-card p-3.5 cursor-pointer transition-all border-l-4 ${
                    isSelected
                      ? 'border-[var(--color-matcha)] bg-[var(--bg-card-alt)] shadow-xs'
                      : 'border-transparent hover:bg-[var(--bg-card-alt)]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[10px] font-mono font-bold text-[var(--text-muted)]">
                      {suite.id} • {suite.category}
                    </span>
                    <span
                      className={`px-2 py-0.2 rounded text-[10px] font-mono font-bold ${
                        suite.status === 'PASS'
                          ? 'badge-matcha'
                          : suite.status === 'FAIL'
                          ? 'badge-dark-red'
                          : 'badge-orange'
                      }`}
                    >
                      {suite.status}
                    </span>
                  </div>

                  <h3 className="font-bold text-xs sm:text-sm text-[var(--text-primary)] mb-1">
                    {suite.name}
                  </h3>

                  <div className="flex items-center justify-between text-[11px] font-mono text-[var(--text-muted)] pt-2 border-t border-[var(--border-subtle)]">
                    <span>{suite.project}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        runTestSuite(suite.id);
                      }}
                      disabled={suite.status === 'RUNNING'}
                      className="px-2 py-0.5 btn-outline text-[10px] flex items-center gap-1 hover:border-[var(--color-matcha)] hover:text-[var(--color-matcha)]"
                    >
                      {suite.status === 'RUNNING' ? (
                        <RotateCw className="w-3 h-3 animate-spin text-[var(--color-orange)]" />
                      ) : (
                        <Play className="w-3 h-3 fill-current" />
                      )}
                      <span>Run</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Console Terminal Inspector */}
        <div className="lg:col-span-2 space-y-4">
          {activeSuite && (
            <div className="app-card overflow-hidden">
              {/* Console Header */}
              <div className="p-4 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <FlaskConical className="w-4 h-4 text-[var(--color-matcha)]" />
                    <h2 className="font-bold text-sm text-[var(--text-primary)]">
                      {activeSuite.name}
                    </h2>
                  </div>
                  <p className="text-xs text-[var(--text-muted)] font-mono mt-0.5">
                    ID: {activeSuite.id} • Executor: {activeSuite.executor} • Pass Rate: {activeSuite.passRate}%
                  </p>
                </div>

                <button
                  onClick={() => runTestSuite(activeSuite.id)}
                  disabled={activeSuite.status === 'RUNNING'}
                  className="btn-matcha px-3 py-1.5 text-xs font-mono font-bold flex items-center gap-1.5"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Re-run Suite</span>
                </button>
              </div>

              {/* Execution Steps Breakdown */}
              <div className="p-4 space-y-3">
                <h3 className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
                  Assertion Steps & Log Trace
                </h3>

                <div className="space-y-2">
                  {activeSuite.steps.map((step, idx) => (
                    <div
                      key={step.id}
                      className="p-3 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded-md font-mono text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-[var(--text-muted)] font-bold">#{idx + 1}</span>
                          <span className="font-bold text-[var(--text-primary)]">{step.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-[var(--text-muted)]">{step.durationMs}ms</span>
                          <span
                            className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                              step.status === 'PASSED'
                                ? 'badge-matcha'
                                : step.status === 'FAILED'
                                ? 'badge-dark-red'
                                : 'badge-orange'
                            }`}
                          >
                            {step.status}
                          </span>
                        </div>
                      </div>

                      {step.logs && (
                        <div className="mt-2 p-2 bg-[var(--text-primary)] text-[var(--bg-main)] rounded text-[11px] font-mono leading-relaxed overflow-x-auto">
                          <code>{step.logs}</code>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Simulated Live Terminal Console Output */}
                <div className="mt-4 p-4 bg-black text-green-400 font-mono text-xs rounded-lg space-y-1 max-h-48 overflow-y-auto custom-scrollbar">
                  <p className="text-gray-500">--- TestOps Pro Runner v2.4.1 ---</p>
                  <p>[INFO] Environment sandbox initialized for {activeSuite.project}</p>
                  <p>[INFO] Executing runner worker node {activeSuite.executor}</p>
                  <p className="text-yellow-400">[TRACE] Hook loaded successfully. Starting assertions...</p>
                  <p className="text-emerald-400">[STATUS] All system assertion checks finished.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
