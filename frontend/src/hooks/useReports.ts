import { useState, useCallback } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { reportsService } from '@/services/reportsService';
import type { AnalyticsData } from '@/services/reportsService';

interface UseReportsReturn {
  analytics: AnalyticsData | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
  exportCsv: () => Promise<void>;
}

/**
 * Hook for fetching analytics data for the reports/charts page.
 * Polls at a slow interval since analytics don't change rapidly.
 */
export function useReports(): UseReportsReturn {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      const result = await reportsService.getAnalytics();
      setAnalytics(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchAnalytics, {
    interval: POLLING_INTERVALS.SLOW,
    enabled: true,
  });

  const exportCsv = useCallback(async () => {
    try {
      const blob = await reportsService.exportCsv();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test-results-${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export CSV');
    }
  }, []);

  return {
    analytics,
    isLoading,
    error,
    refresh,
    exportCsv,
  };
}
