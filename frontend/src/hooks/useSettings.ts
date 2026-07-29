import { useState, useCallback, useEffect } from 'react';
import { settingsService } from '@/services/settingsService';
import type { Settings, SettingsUpdateRequest } from '@/services/settingsService';

interface UseSettingsReturn {
  settings: Settings | null;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  updateSettings: (updates: SettingsUpdateRequest) => Promise<void>;
  refresh: () => void;
}

/**
 * Hook for reading and writing application settings.
 * Fetches once on mount (no polling — settings are rarely changed externally).
 */
export function useSettings(): UseSettingsReturn {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = useCallback(async () => {
    try {
      const result = await settingsService.get();
      setSettings(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const updateSettings = useCallback(async (updates: SettingsUpdateRequest) => {
    setIsSaving(true);
    try {
      const updated = await settingsService.update(updates);
      setSettings(updated);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, []);

  return {
    settings,
    isLoading,
    error,
    isSaving,
    updateSettings,
    refresh: fetchSettings,
  };
}
