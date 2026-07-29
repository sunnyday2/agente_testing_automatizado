import { Inbox } from 'lucide-react';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="w-12 h-12 rounded-full bg-[var(--bg-card-alt)] flex items-center justify-center mb-4">
        {icon || <Inbox className="w-6 h-6 text-[var(--text-muted)]" />}
      </div>
      <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1">{title}</h3>
      {description && (
        <p className="text-xs text-[var(--text-muted)] max-w-xs mb-4">{description}</p>
      )}
      {action}
    </div>
  );
}
