import { api } from './apiClient';
import type { TestSuite } from '@/types';

export const testSuitesService = {
  async getAll(): Promise<TestSuite[]> {
    const { data } = await api.get<{ data: TestSuite[]; total: number }>('/test-suites');
    return data.data;
  },

  async getById(id: string): Promise<TestSuite> {
    const { data } = await api.get<{ data: TestSuite }>(`/test-suites/${id}`);
    return data.data;
  },

  async run(id: string): Promise<TestSuite> {
    const { data } = await api.post<{ data: TestSuite }>(`/test-suites/${id}/run`);
    return data.data;
  },

  async scan(): Promise<TestSuite[]> {
    const { data } = await api.post<{ data: TestSuite[]; total: number }>('/test-suites/scan');
    return data.data;
  },
};
