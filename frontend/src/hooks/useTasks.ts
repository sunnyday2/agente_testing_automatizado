import { useState, useCallback } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { tasksService } from '@/services/tasksService';
import type { ApiTask } from '@/services/tasksService';
import type { ColumnType } from '@/types';

interface UseTasksReturn {
  tasks: ApiTask[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
  createTask: (task: Parameters<typeof tasksService.create>[0]) => Promise<void>;
  updateTask: (id: string, updates: Parameters<typeof tasksService.update>[1]) => Promise<void>;
  moveTask: (id: string, column: ColumnType) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
}

/**
 * Hook for Kanban board task CRUD operations.
 * Provides optimistic updates for move and delete, with rollback on failure.
 */
export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<ApiTask[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const result = await tasksService.getAll();
      setTasks(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchTasks, {
    interval: POLLING_INTERVALS.SLOW,
    enabled: true,
  });

  const createTask = useCallback(async (taskData: Parameters<typeof tasksService.create>[0]) => {
    try {
      const created = await tasksService.create(taskData);
      setTasks(prev => [created, ...prev]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      throw err;
    }
  }, []);

  const updateTask = useCallback(async (id: string, updates: Parameters<typeof tasksService.update>[1]) => {
    // Optimistic update
    const previousTasks = tasks;
    setTasks(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t));

    try {
      const updated = await tasksService.update(id, updates);
      setTasks(prev => prev.map(t => t.id === id ? updated : t));
      setError(null);
    } catch (err) {
      // Rollback on failure
      setTasks(previousTasks);
      setError(err instanceof Error ? err.message : 'Failed to update task');
      throw err;
    }
  }, [tasks]);

  const moveTask = useCallback(async (id: string, column: ColumnType) => {
    // Optimistic update
    const previousTasks = tasks;
    setTasks(prev => prev.map(t => t.id === id ? { ...t, column_name: column } : t));

    try {
      const updated = await tasksService.move(id, column);
      setTasks(prev => prev.map(t => t.id === id ? updated : t));
      setError(null);
    } catch (err) {
      // Rollback on failure
      setTasks(previousTasks);
      setError(err instanceof Error ? err.message : 'Failed to move task');
      throw err;
    }
  }, [tasks]);

  const deleteTask = useCallback(async (id: string) => {
    // Optimistic removal
    const previousTasks = tasks;
    setTasks(prev => prev.filter(t => t.id !== id));

    try {
      await tasksService.delete(id);
      setError(null);
    } catch (err) {
      // Rollback on failure
      setTasks(previousTasks);
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      throw err;
    }
  }, [tasks]);

  return {
    tasks,
    isLoading,
    error,
    refresh,
    createTask,
    updateTask,
    moveTask,
    deleteTask,
  };
}
