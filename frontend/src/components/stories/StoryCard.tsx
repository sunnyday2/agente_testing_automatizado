import { CheckCircle2, Clock, Trash2, Eye } from 'lucide-react';
import type { Story } from '@/services/storiesService';

interface StoryCardProps {
  story: Story;
  onView: (story: Story) => void;
  onDelete: (id: string) => void;
}

export function StoryCard({ story, onView, onDelete }: StoryCardProps) {
  return (
    <div className="app-card p-4 flex flex-col justify-between group">
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-[var(--bg-card-alt)] text-[var(--text-primary)] border border-[var(--border-color)]">
            {story.format}
          </span>
          <div className="flex items-center gap-1">
            {story.is_indexed ? (
              <span className="badge-matcha px-1.5 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Indexed
              </span>
            ) : (
              <span className="badge-orange px-1.5 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1">
                <Clock className="w-3 h-3" /> Pending
              </span>
            )}
          </div>
        </div>

        <h4 className="text-sm font-bold text-[var(--text-primary)] leading-tight mb-1 line-clamp-2">
          {story.title}
        </h4>

        <div className="flex flex-wrap gap-1.5 mt-2">
          {story.epic && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
              {story.epic}
            </span>
          )}
          {story.feature && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
              {story.feature}
            </span>
          )}
          {story.target_role && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
              {story.target_role}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 mt-3 border-t border-[var(--border-subtle)] text-[11px] font-mono">
        <span className="text-[var(--text-muted)]">
          {story.test_scenarios_count} scenarios
        </span>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onView(story)}
            className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            title="View story"
            aria-label={`View story: ${story.title}`}
          >
            <Eye className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onDelete(story.id)}
            className="p-1 text-[var(--text-muted)] hover:text-[var(--color-dark-red)]"
            title="Delete story"
            aria-label={`Delete story: ${story.title}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
