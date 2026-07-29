import { useState, useCallback, useRef } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { testSuitesService } from '@/services/testSuitesService';
import type { TestSuite } from '@/types';

interface UseTestSuitesReturn {
  suites: TestSuite[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
  runSuite: (id: string) => Promise<void>;
  selectedSuite: TestSuite | null;
  selectSuite: (id: string) => void;
}

/**
 * Hook for test suite management.
 * Polls faster (3s) when any suite is in RUNNING state to show real-time updates.
 */
export function useTestSuites(): UseTestSuitesReturn {
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSuiteId, setSelectedSuiteId] = useState<string | null>(null);
  const hasRunningSuite = useRef(false);

  const fetchSuites = useCallback(async () => {
    try {
      const result = await testSuitesService.getAll();
      setSuites(result);
      hasRunningSuite.current = result.some(s => s.status === 'RUNNING');
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch test suites');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Poll faster when a suite is running
  const { refresh } = usePolling(fetchSuites, {
    interval: hasRunningSuite.current ? POLLING_INTERVALS.FAST : POLLING_INTERVALS.NORMAL,
    enabled: true,
  });

  const runSuite = useCallback(async (id: string) => {
    // Optimistic: mark as RUNNING immediately
    setSuites(prev => prev.map(s =>
      s.id === id ? { ...s, status: 'RUNNING' as const, lastRun: 'Running now...' } : s
    ));
    hasRunningSuite.current = true;

    try {
      const updated = await testSuitesService.run(id);
      setSuites(prev => prev.map(s => s.id === id ? updated : s));
      setError(null);
    } catch (err) {
      // Revert on failure
      setError(err instanceof Error ? err.message : 'Failed to run suite');
      refresh();
    }
  }, [refresh]);

  const selectSuite = useCallback((id: string) => {
    setSelectedSuiteId(id);
  }, []);

  const selectedSuite = suites.find(s => s.id === selectedSuiteId) ?? suites[0] ?? null;

  return {
    suites,
    isLoading,
    error,
    refresh,
    runSuite,
    selectedSuite,
    selectSuite,
  };
}
