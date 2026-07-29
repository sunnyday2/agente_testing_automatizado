import { Modal } from '@/components/shared/Modal';
import { CheckCircle2, Clock, FileText, Code } from 'lucide-react';
import type { Story } from '@/services/storiesService';

interface StoryDetailModalProps {
  story: Story | null;
  isOpen: boolean;
  onClose: () => void;
}

export function StoryDetailModal({ story, isOpen, onClose }: StoryDetailModalProps) {
  if (!story) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={story.title} maxWidth="max-w-2xl">
      <div className="space-y-4">
        {/* Metadata row */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[var(--bg-card-alt)] border border-[var(--border-color)]">
            {story.format === 'markdown' ? <FileText className="w-3 h-3" /> : <Code className="w-3 h-3" />}
            {story.format.toUpperCase()}
          </span>
          {story.is_indexed ? (
            <span className="badge-matcha px-2 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Indexed in ChromaDB
            </span>
          ) : (
            <span className="badge-orange px-2 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1">
              <Clock className="w-3 h-3" /> Not yet indexed
            </span>
          )}
          {story.test_scenarios_count > 0 && (
            <span className="text-[10px] font-mono font-bold text-[var(--text-muted)]">
              {story.test_scenarios_count} test scenarios generated
            </span>
          )}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {story.epic && (
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border border-[var(--border-color)]">
              Epic: {story.epic}
            </span>
          )}
          {story.feature && (
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border border-[var(--border-color)]">
              Feature: {story.feature}
            </span>
          )}
          {story.target_role && (
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border border-[var(--border-color)]">
              Role: {story.target_role}
            </span>
          )}
        </div>

        {/* Content */}
        <div className="p-4 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded max-h-80 overflow-y-auto custom-scrollbar">
          <pre className="text-xs font-mono text-[var(--text-primary)] whitespace-pre-wrap leading-relaxed">
            {story.content}
          </pre>
        </div>

        {/* Footer */}
        <div className="text-[10px] font-mono text-[var(--text-muted)] pt-2 border-t border-[var(--border-color)]">
          Created: {story.created_at ? new Date(story.created_at).toLocaleString() : 'Unknown'}
        </div>
      </div>
    </Modal>
  );
}
