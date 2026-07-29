import { useState } from 'react';
import { Upload, FileText, Code } from 'lucide-react';
import type { StoryCreateRequest } from '@/services/storiesService';

interface StoryUploadFormProps {
  onSubmit: (data: StoryCreateRequest) => Promise<void>;
  isSubmitting?: boolean;
}

export function StoryUploadForm({ onSubmit, isSubmitting = false }: StoryUploadFormProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [format, setFormat] = useState<'markdown' | 'json'>('markdown');
  const [epic, setEpic] = useState('');
  const [feature, setFeature] = useState('');
  const [targetRole, setTargetRole] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    await onSubmit({
      title: title.trim(),
      content: content.trim(),
      format,
      epic: epic.trim() || undefined,
      feature: feature.trim() || undefined,
      target_role: targetRole.trim() || undefined,
    });

    // Reset form on success
    setTitle('');
    setContent('');
    setEpic('');
    setFeature('');
    setTargetRole('');
  };

  return (
    <form onSubmit={handleSubmit} className="app-card p-5 space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-[var(--border-color)]">
        <Upload className="w-4 h-4 text-[var(--color-matcha)]" />
        <h3 className="font-bold text-sm text-[var(--text-primary)]">Add User Story</h3>
      </div>

      <div>
        <label htmlFor="story-title" className="block text-xs font-mono font-bold uppercase mb-1">
          Title <span className="text-[var(--color-dark-red)]">*</span>
        </label>
        <input
          id="story-title"
          type="text"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. User can reset password via email"
          className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
        />
      </div>

      {/* Format toggle */}
      <div>
        <label className="block text-xs font-mono font-bold uppercase mb-1.5">Format</label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setFormat('markdown')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded border transition-colors ${
              format === 'markdown'
                ? 'bg-[var(--text-primary)] text-[var(--bg-card)] border-[var(--text-primary)] font-bold'
                : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border-[var(--border-color)] hover:border-[var(--text-secondary)]'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> Markdown
          </button>
          <button
            type="button"
            onClick={() => setFormat('json')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded border transition-colors ${
              format === 'json'
                ? 'bg-[var(--text-primary)] text-[var(--bg-card)] border-[var(--text-primary)] font-bold'
                : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border-[var(--border-color)] hover:border-[var(--text-secondary)]'
            }`}
          >
            <Code className="w-3.5 h-3.5" /> JSON
          </button>
        </div>
      </div>

      <div>
        <label htmlFor="story-content" className="block text-xs font-mono font-bold uppercase mb-1">
          Content <span className="text-[var(--color-dark-red)]">*</span>
        </label>
        <textarea
          id="story-content"
          required
          rows={6}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={format === 'markdown'
            ? '## User Story\n\nAs a [user],\nI want to [action],\nSo that [benefit].\n\n## Acceptance Criteria\n- ...'
            : '{\n  "as_a": "user",\n  "i_want": "to reset my password",\n  "so_that": "I can regain account access"\n}'
          }
          className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm font-mono text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
        />
      </div>

      {/* Metadata fields */}
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label htmlFor="story-epic" className="block text-xs font-mono font-bold uppercase mb-1">Epic</label>
          <input
            id="story-epic"
            type="text"
            value={epic}
            onChange={(e) => setEpic(e.target.value)}
            placeholder="e.g. Auth"
            className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
          />
        </div>
        <div>
          <label htmlFor="story-feature" className="block text-xs font-mono font-bold uppercase mb-1">Feature</label>
          <input
            id="story-feature"
            type="text"
            value={feature}
            onChange={(e) => setFeature(e.target.value)}
            placeholder="e.g. Password Reset"
            className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
          />
        </div>
        <div>
          <label htmlFor="story-role" className="block text-xs font-mono font-bold uppercase mb-1">Role</label>
          <input
            id="story-role"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. End User"
            className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !title.trim() || !content.trim()}
        className="w-full py-2.5 btn-matcha text-xs font-mono font-bold flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Upload className="w-4 h-4" />
        <span>{isSubmitting ? 'Saving...' : 'Add Story'}</span>
      </button>
    </form>
  );
}
