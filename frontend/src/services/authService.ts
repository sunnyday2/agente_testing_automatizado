import { api } from './apiClient';

interface LoginRequest {
  email: string;
  password: string;
}

interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at?: string;
}

interface LoginResponse {
  status: string;
  data: UserResponse;
}

interface AuthStatusResponse {
  status: string;
  data: UserResponse;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<UserResponse> {
    const { data } = await api.post<LoginResponse>('/auth/login', credentials);
    return data.data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  async getMe(): Promise<UserResponse> {
    const { data } = await api.get<AuthStatusResponse>('/auth/me');
    return data.data;
  },
};

export type { UserResponse, LoginRequest };
