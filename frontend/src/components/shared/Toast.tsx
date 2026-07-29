import { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  /** Auto-dismiss after ms (0 = manual dismiss only) */
  duration?: number;
  onClose: () => void;
}

export function Toast({ message, type = 'info', duration = 4000, onClose }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const iconMap = {
    success: <CheckCircle2 className="w-4 h-4 text-[var(--color-matcha)]" />,
    error: <AlertCircle className="w-4 h-4 text-[var(--color-dark-red)]" />,
    info: <Info className="w-4 h-4 text-[var(--color-orange)]" />,
  };

  const borderMap = {
    success: 'border-l-[var(--color-matcha)]',
    error: 'border-l-[var(--color-dark-red)]',
    info: 'border-l-[var(--color-orange)]',
  };

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 app-card p-3 shadow-lg border-l-4 ${borderMap[type]} flex items-center gap-3 max-w-sm animate-in`}
      role="alert"
    >
      {iconMap[type]}
      <p className="text-xs text-[var(--text-primary)] flex-1">{message}</p>
      <button
        onClick={onClose}
        className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
