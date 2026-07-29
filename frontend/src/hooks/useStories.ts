import { useState, useCallback } from 'react';
import { usePolling, POLLING_INTERVALS } from './usePolling';
import { storiesService } from '@/services/storiesService';
import type { Story, StoryCreateRequest } from '@/services/storiesService';

interface UseStoriesReturn {
  stories: Story[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
  createStory: (data: StoryCreateRequest) => Promise<void>;
  deleteStory: (id: string) => Promise<void>;
  seedStories: (reset?: boolean) => Promise<number>;
  isSeedingInProgress: boolean;
}

/**
 * Hook for user story management and RAG indexing operations.
 */
export function useStories(): UseStoriesReturn {
  const [stories, setStories] = useState<Story[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSeedingInProgress, setIsSeedingInProgress] = useState(false);

  const fetchStories = useCallback(async () => {
    try {
      const result = await storiesService.getAll();
      setStories(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stories');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { refresh } = usePolling(fetchStories, {
    interval: POLLING_INTERVALS.SLOW,
    enabled: true,
  });

  const createStory = useCallback(async (data: StoryCreateRequest) => {
    try {
      const created = await storiesService.create(data);
      setStories(prev => [created, ...prev]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create story');
      throw err;
    }
  }, []);

  const deleteStory = useCallback(async (id: string) => {
    const previous = stories;
    setStories(prev => prev.filter(s => s.id !== id));

    try {
      await storiesService.delete(id);
      setError(null);
    } catch (err) {
      setStories(previous);
      setError(err instanceof Error ? err.message : 'Failed to delete story');
      throw err;
    }
  }, [stories]);

  const seedStories = useCallback(async (reset = false): Promise<number> => {
    setIsSeedingInProgress(true);
    try {
      const result = await storiesService.seed(reset);
      // Refresh to get updated indexed status
      await fetchStories();
      setError(null);
      return result.stories_indexed;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to seed stories');
      throw err;
    } finally {
      setIsSeedingInProgress(false);
    }
  }, [fetchStories]);

  return {
    stories,
    isLoading,
    error,
    refresh,
    createStory,
    deleteStory,
    seedStories,
    isSeedingInProgress,
  };
}
