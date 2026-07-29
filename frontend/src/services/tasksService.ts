import { api } from './apiClient';
import type { ColumnType } from '@/types';

interface TaskCreateRequest {
  title: string;
  description: string;
  category: string;
  business_group: string;
  priority: string;
  column_name: ColumnType;
  due_date?: string;
  tags?: string[];
}

interface TaskUpdateRequest {
  title?: string;
  description?: string;
  category?: string;
  priority?: string;
  column_name?: ColumnType;
  due_date?: string;
}

/** Backend response wrapper for list endpoints */
interface ListResponse<T> {
  status: string;
  data: T[];
  total: number;
}

/** Backend response wrapper for detail endpoints */
interface DetailResponse<T> {
  status: string;
  data: T;
  message?: string;
}

/** Task as returned by the backend API (snake_case) */
interface ApiTask {
  id: string;
  title: string;
  description: string | null;
  category: string | null;
  business_group: string | null;
  priority: string;
  column_name: string;
  project_id: string | null;
  due_date: string | null;
  tags: string[] | null;
  plane_task_id: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export const tasksService = {
  async getAll(): Promise<ApiTask[]> {
    const { data } = await api.get<ListResponse<ApiTask>>('/tasks');
    return data.data;
  },

  async create(task: TaskCreateRequest): Promise<ApiTask> {
    const { data } = await api.post<DetailResponse<ApiTask>>('/tasks', task);
    return data.data;
  },

  async update(id: string, updates: TaskUpdateRequest): Promise<ApiTask> {
    const { data } = await api.patch<DetailResponse<ApiTask>>(`/tasks/${id}`, updates);
    return data.data;
  },

  async move(id: string, column: ColumnType): Promise<ApiTask> {
    const { data } = await api.patch<DetailResponse<ApiTask>>(`/tasks/${id}/move`, { column_name: column });
    return data.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/tasks/${id}`);
  },
};

export type { ApiTask, TaskCreateRequest, TaskUpdateRequest };
