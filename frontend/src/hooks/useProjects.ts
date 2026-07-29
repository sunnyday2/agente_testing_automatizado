import { useState, useCallback } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { projectsService } from '@/services/projectsService';
import type { Project } from '@/types';

interface UseProjectsReturn {
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
  createProject: (data: Parameters<typeof projectsService.create>[0]) => Promise<void>;
  updateProject: (id: string, updates: Parameters<typeof projectsService.update>[1]) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
}

/**
 * Hook for project CRUD operations.
 * Polls at a slow interval since projects change infrequently.
 */
export function useProjects(): UseProjectsReturn {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    try {
      const result = await projectsService.getAll();
      setProjects(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchProjects, {
    interval: POLLING_INTERVALS.SLOW,
    enabled: true,
  });

  const createProject = useCallback(async (data: Parameters<typeof projectsService.create>[0]) => {
    try {
      const created = await projectsService.create(data);
      setProjects(prev => [created, ...prev]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      throw err;
    }
  }, []);

  const updateProject = useCallback(async (id: string, updates: Parameters<typeof projectsService.update>[1]) => {
    try {
      const updated = await projectsService.update(id, updates);
      setProjects(prev => prev.map(p => p.id === id ? updated : p));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project');
      throw err;
    }
  }, []);

  const deleteProject = useCallback(async (id: string) => {
    const previous = projects;
    setProjects(prev => prev.filter(p => p.id !== id));

    try {
      await projectsService.delete(id);
      setError(null);
    } catch (err) {
      setProjects(previous);
      setError(err instanceof Error ? err.message : 'Failed to delete project');
      throw err;
    }
  }, [projects]);

  return {
    projects,
    isLoading,
    error,
    refresh,
    createProject,
    updateProject,
    deleteProject,
  };
}
