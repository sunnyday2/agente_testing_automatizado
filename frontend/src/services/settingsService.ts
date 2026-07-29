import { api } from './apiClient';

interface Settings {
  slack_webhook_url: string;
  email_alerts_enabled: boolean;
  api_key: string;
  git_mode: 'commit-only' | 'commit-and-push' | 'disabled';
  test_browser: 'chromium' | 'firefox' | 'webkit';
  test_headless: boolean;
}

interface SettingsUpdateRequest {
  slack_webhook_url?: string;
  email_alerts_enabled?: boolean;
  git_mode?: string;
  test_browser?: string;
  test_headless?: boolean;
}

export const settingsService = {
  async get(): Promise<Settings> {
    const { data } = await api.get<{ data: Record<string, string> }>('/settings');
    // Map from backend key-value pairs to typed Settings object
    const raw = data.data;
    return {
      slack_webhook_url: raw['slack_webhook_url'] ?? '',
      email_alerts_enabled: raw['email_alerts_enabled'] === 'true',
      api_key: raw['api_key'] ?? '',
      git_mode: (raw['git_mode'] as Settings['git_mode']) ?? 'commit-only',
      test_browser: (raw['test_browser'] as Settings['test_browser']) ?? 'chromium',
      test_headless: raw['test_headless'] !== 'false',
    };
  },

  async update(updates: SettingsUpdateRequest): Promise<Settings> {
    // Convert to key-value pairs for the backend
    const settings: Record<string, string> = {};
    if (updates.slack_webhook_url !== undefined) settings['slack_webhook_url'] = updates.slack_webhook_url;
    if (updates.email_alerts_enabled !== undefined) settings['email_alerts_enabled'] = String(updates.email_alerts_enabled);
    if (updates.git_mode !== undefined) settings['git_mode'] = updates.git_mode;
    if (updates.test_browser !== undefined) settings['test_browser'] = updates.test_browser;
    if (updates.test_headless !== undefined) settings['test_headless'] = String(updates.test_headless);

    await api.patch<{ data: Record<string, string> }>('/settings', { settings });
    return settingsService.get();
  },
};

export type { Settings, SettingsUpdateRequest };
