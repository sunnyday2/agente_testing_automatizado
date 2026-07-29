import { api } from './apiClient';

interface OverviewStats {
  total_tests: number;
  passed: number;
  failed: number;
  in_progress: number;
  pass_rate: number;
  velocity_tests_per_day: number;
  velocity_trend: number;
}

interface VelocityDataPoint {
  day: string;
  passed: number;
  failed: number;
  in_progress: number;
}

interface FailureCategory {
  name: string;
  value: number;
  color: string;
}

interface PassRateByEnv {
  env: string;
  rate: number;
}

interface AnalyticsData {
  velocity: VelocityDataPoint[];
  failures: FailureCategory[];
  pass_rate_by_env: PassRateByEnv[];
}

export const reportsService = {
  async getOverviewStats(): Promise<OverviewStats> {
    const { data } = await api.get<{ data: OverviewStats }>('/stats/overview');
    return data.data;
  },

  async getAnalytics(): Promise<AnalyticsData> {
    const { data } = await api.get<AnalyticsData>('/reports/analytics');
    return data;
  },

  async exportCsv(): Promise<Blob> {
    const response = await fetch('/reports/export-csv', {
      credentials: 'include',
    });
    return response.blob();
  },
};

export type {
  OverviewStats,
  VelocityDataPoint,
  FailureCategory,
  PassRateByEnv,
  AnalyticsData,
};
