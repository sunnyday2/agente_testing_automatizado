import { useEffect, useRef, useCallback } from 'react';

interface UsePollingOptions {
  /** Polling interval in milliseconds */
  interval: number;
  /** Whether polling is active */
  enabled?: boolean;
  /** Call immediately on mount before first interval */
  immediate?: boolean;
}

interface UsePollingReturn {
  /** Manually trigger a refresh */
  refresh: () => void;
}

/**
 * Generic polling hook. Calls the provided function at a regular interval.
 * Automatically cleans up on unmount or when disabled.
 */
export function usePolling(
  fn: () => Promise<void> | void,
  options: UsePollingOptions
): UsePollingReturn {
  const { interval, enabled = true, immediate = true } = options;
  const fnRef = useRef(fn);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Keep fn reference fresh without re-triggering effect
  fnRef.current = fn;

  const refresh = useCallback(() => {
    fnRef.current();
  }, []);

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    if (immediate) {
      fnRef.current();
    }

    intervalRef.current = setInterval(() => {
      fnRef.current();
    }, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [interval, enabled, immediate]);

  return { refresh };
}

/** Standard polling intervals */
export const POLLING_INTERVALS = {
  FAST: 3000,
  NORMAL: 5000,
  SLOW: 15000,
  REALTIME: 1000,
} as const;
