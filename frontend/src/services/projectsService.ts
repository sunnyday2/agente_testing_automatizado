import { api } from './apiClient';
import type { Project } from '@/types';

interface ProjectCreateRequest {
  name: string;
  subtitle: string;
  environment: 'Production' | 'Staging' | 'Dev';
  visibility: 'Public' | 'Private';
  integrations: {
    jenkins: boolean;
    slack: boolean;
    jira: boolean;
    s3: boolean;
  };
}

export const projectsService = {
  async getAll(): Promise<Project[]> {
    const { data } = await api.get<{ data: Project[]; total: number }>('/projects');
    return data.data;
  },

  async create(project: ProjectCreateRequest): Promise<Project> {
    const { data } = await api.post<{ data: Project }>('/projects', project);
    return data.data;
  },

  async update(id: string, updates: Partial<ProjectCreateRequest>): Promise<Project> {
    const { data } = await api.patch<{ data: Project }>(`/projects/${id}`, updates);
    return data.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/projects/${id}`);
  },
};
