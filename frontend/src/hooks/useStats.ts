import { useState, useCallback } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { reportsService } from '@/services/reportsService';
import type { OverviewStats } from '@/services/reportsService';

interface UseStatsReturn {
  stats: OverviewStats | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Hook for fetching dashboard overview statistics.
 * Polls the /api/stats/overview endpoint at a normal interval.
 */
export function useStats(): UseStatsReturn {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const result = await reportsService.getOverviewStats();
      setStats(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchStats, {
    interval: POLLING_INTERVALS.NORMAL,
    enabled: true,
  });

  return { stats, isLoading, error, refresh };
}
