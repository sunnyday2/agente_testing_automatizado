import React, { useState } from 'react';
import { TaskCard, ColumnType, CategoryTag, Priority } from '@/types';
import { X, Check } from 'lucide-react';

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (taskData: Omit<TaskCard, 'id'> | TaskCard) => void;
  initialTask?: TaskCard | null;
  defaultColumn?: ColumnType;
}

export const TaskModal: React.FC<TaskModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialTask,
  defaultColumn = 'TO DO',
}) => {
  const [title, setTitle] = useState(initialTask?.title || '');
  const [description, setDescription] = useState(initialTask?.description || '');
  const [category, setCategory] = useState(initialTask?.category || 'OPERATIONS');
  const [businessGroup, setBusinessGroup] = useState<CategoryTag>(initialTask?.businessGroup || 'AI Native Business');
  const [priority, setPriority] = useState<Priority>(initialTask?.priority || 'MEDIUM');
  const [column, setColumn] = useState<ColumnType>(initialTask?.column || defaultColumn);
  const [dueDate, setDueDate] = useState(initialTask?.dueDate || '');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    if (initialTask) {
      onSave({
        ...initialTask,
        title,
        description,
        category: category.toUpperCase(),
        businessGroup,
        priority,
        column,
        dueDate: dueDate || undefined,
      });
    } else {
      onSave({
        title,
        description,
        category: category.toUpperCase(),
        businessGroup,
        priority,
        column,
        dueDate: dueDate || undefined,
        assignees: [],
        tags: [category.toLowerCase()],
      });
    }
    onClose();
  };

  const columns: ColumnType[] = [
    'IDEAS / PLANNING',
    'BACKLOG',
    'TO DO',
    'IN PROGRESS',
    'REVIEW / TESTING',
    'DONE',
  ];

  const categories: CategoryTag[] = [
    'AI Native Business',
    'AI Professionals Network',
    'Practical AI For Business',
    'AI Book Coach',
    'The Mum Project',
    'The Bridge Podcast',
    'Operations',
    'Other',
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="app-card w-full max-w-lg shadow-2xl p-6 relative bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-primary)]">
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-[var(--border-color)]">
          <h3 className="font-bold text-base md:text-lg">
            {initialTask ? 'Edit Task Item' : 'Create New Task Item'}
          </h3>
          <button
            onClick={onClose}
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] p-1 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold uppercase mb-1">
              Title <span className="text-[var(--color-dark-red)]">*</span>
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Upload 'The Human Gap' white paper"
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-bold uppercase mb-1">
              Description
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide context, acceptance criteria or links..."
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Category Tag
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="OPERATIONS, MOBILE-QA..."
                className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              />
            </div>

            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Business Stream
              </label>
              <select
                value={businessGroup}
                onChange={(e) => setBusinessGroup(e.target.value as CategoryTag)}
                className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as Priority)}
                className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              >
                <option value="HIGH">HIGH (Dark Red)</option>
                <option value="MEDIUM">MEDIUM (Orange / Ochre)</option>
                <option value="LOW">LOW (Matcha / Light Green)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Column
              </label>
              <select
                value={column}
                onChange={(e) => setColumn(e.target.value as ColumnType)}
                className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              >
                {columns.map((col) => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono font-bold uppercase mb-1">
              Due Date (Optional)
            </label>
            <input
              type="text"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              placeholder="e.g. 18 May or 2026-08-01"
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
          </div>

          <div className="pt-4 flex justify-end gap-2 border-t border-[var(--border-color)]">
            <button
              type="button"
              onClick={onClose}
              className="btn-outline px-4 py-2 text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-matcha px-5 py-2 text-xs flex items-center gap-1.5 shadow-sm"
            >
              <Check className="w-4 h-4" />
              <span>{initialTask ? 'Save Changes' : 'Create Task'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
