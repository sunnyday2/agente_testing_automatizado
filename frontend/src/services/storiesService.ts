import { api } from './apiClient';

interface Story {
  id: string;
  title: string;
  content: string;
  format: 'markdown' | 'json';
  epic: string;
  feature: string;
  target_role: string;
  is_indexed: boolean;
  test_scenarios_count: number;
  created_at: string;
}

interface StoryCreateRequest {
  title: string;
  content: string;
  format: 'markdown' | 'json';
  epic?: string;
  feature?: string;
  target_role?: string;
}

export const storiesService = {
  async getAll(): Promise<Story[]> {
    const { data } = await api.get<{ data: Story[]; total: number }>('/stories');
    return data.data;
  },

  async create(story: StoryCreateRequest): Promise<Story> {
    const { data } = await api.post<{ data: Story }>('/stories', story);
    return data.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/stories/${id}`);
  },

  async seed(reset = false): Promise<{ stories_indexed: number }> {
    const { data } = await api.post<{ stories_indexed: number }>('/stories/seed', { reset });
    return data;
  },
};

export type { Story, StoryCreateRequest };
