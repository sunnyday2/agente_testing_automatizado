/**
 * Base API client for communicating with the FastAPI backend.
 * All service modules use this client — never call fetch() directly in components.
 */

interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

interface ApiResponse<T> {
  data: T;
  status: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`;

    const response = await fetch(url, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (response.status === 401) {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      throw new Error('Unauthorized — please log in again.');
    }

    if (!response.ok) {
      const errorBody: ApiError = await response.json().catch(() => ({
        error: 'NetworkError',
        message: `Request failed with status ${response.status}`,
      }));
      throw new Error(errorBody.message || `API error: ${response.status}`);
    }

    if (response.status === 204) {
      return { data: undefined as unknown as T, status: 204 };
    }

    const data: T = await response.json();
    return { data, status: response.status };
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });
  }

  async delete(path: string): Promise<void> {
    await this.request(path, { method: 'DELETE' });
  }
}

/** Use for /api/* prefixed endpoints */
export const api = new ApiClient('/api');

/** Use for non-prefixed endpoints (/crawl, /health) */
export const rawApi = new ApiClient('');
