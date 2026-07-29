import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { useTasks } from '@/hooks/useTasks';
import { ColumnType, CategoryTag, TaskCard, Priority } from '@/types';
import { TaskModal } from '@/components/kanban/TaskModal';
import { 
  Plus, 
  Calendar, 
  Trash2, 
  Edit3, 
  ArrowRight, 
  ArrowLeft,
  Download,
  Upload,
  ListFilter,
} from 'lucide-react';

export const KanbanBoard: React.FC = () => {
  const {
    tasks: contextTasks,
    selectedBusinessTag,
    setSelectedBusinessTag,
    viewMode,
    setViewMode,
    searchQuery,
    addTask: contextAddTask,
    updateTask: contextUpdateTask,
    moveTaskColumn: contextMoveTask,
    deleteTask: contextDeleteTask,
    setCurrentView,
  } = useApp();

  // API-backed hook — falls back to context data if API unavailable
  const apiTasks = useTasks();
  const hasApiData = apiTasks.tasks.length > 0 && !apiTasks.error;

  // Use API tasks when available, otherwise context mock data
  const tasks: TaskCard[] = hasApiData
    ? apiTasks.tasks.map(t => ({
        id: t.id,
        title: t.title,
        description: t.description ?? '',
        category: t.category ?? 'OPERATIONS',
        businessGroup: (t.business_group ?? 'Operations') as CategoryTag,
        priority: (t.priority ?? 'MEDIUM') as Priority,
        column: (t.column_name ?? 'TO DO') as ColumnType,
        dueDate: t.due_date ?? undefined,
        assignees: [],
        tags: t.tags ?? [],
      }))
    : contextTasks;

  const addTask = (taskData: Omit<TaskCard, 'id'>) => {
    if (hasApiData) {
      apiTasks.createTask({
        title: taskData.title,
        description: taskData.description,
        category: taskData.category,
        business_group: taskData.businessGroup,
        priority: taskData.priority,
        column_name: taskData.column,
        due_date: taskData.dueDate,
        tags: taskData.tags,
      });
    } else {
      contextAddTask(taskData);
    }
  };

  const updateTask = (task: TaskCard) => {
    if (hasApiData) {
      apiTasks.updateTask(task.id, {
        title: task.title,
        description: task.description,
        category: task.category,
        priority: task.priority,
        column_name: task.column,
        due_date: task.dueDate,
      });
    } else {
      contextUpdateTask(task);
    }
  };

  const moveTaskColumn = (taskId: string, newColumn: ColumnType) => {
    if (hasApiData) {
      apiTasks.moveTask(taskId, newColumn);
    } else {
      contextMoveTask(taskId, newColumn);
    }
  };

  const deleteTask = (taskId: string) => {
    if (hasApiData) {
      apiTasks.deleteTask(taskId);
    } else {
      contextDeleteTask(taskId);
    }
  };

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskCard | null>(null);
  const [defaultAddColumn, setDefaultAddColumn] = useState<ColumnType>('TO DO');

  const businessCategories: CategoryTag[] = [
    'ALL',
    'AI Native Business',
    'AI Professionals Network',
    'Practical AI For Business',
    'AI Book Coach',
    'The Mum Project',
    'The Bridge Podcast',
    'Operations',
    'Other',
  ];

  const columns: { id: ColumnType; title: string; colorClass: string }[] = [
    { id: 'IDEAS / PLANNING', title: 'IDEAS / PLANNING', colorClass: 'border-t-[var(--color-okra)]' },
    { id: 'BACKLOG', title: 'BACKLOG', colorClass: 'border-t-[var(--text-muted)]' },
    { id: 'TO DO', title: 'TO DO', colorClass: 'border-t-[var(--color-orange)]' },
    { id: 'IN PROGRESS', title: 'IN PROGRESS', colorClass: 'border-t-[var(--color-matcha)]' },
    { id: 'REVIEW / TESTING', title: 'REVIEW / TESTING', colorClass: 'border-t-[var(--color-brown)]' },
    { id: 'DONE', title: 'DONE', colorClass: 'border-t-[var(--color-light-green)]' },
  ];

  // Filter tasks by selected tag and search query
  const filteredTasks = tasks.filter((task) => {
    const matchesTag =
      selectedBusinessTag === 'ALL' || task.businessGroup === selectedBusinessTag;
    const matchesSearch =
      !searchQuery ||
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTag && matchesSearch;
  });

  const getPriorityBadgeClass = (priority: Priority) => {
    switch (priority) {
      case 'HIGH':
        return 'badge-dark-red';
      case 'MEDIUM':
        return 'badge-orange';
      case 'LOW':
        return 'badge-matcha';
      default:
        return 'badge-okra';
    }
  };

  const handleOpenAddModal = (col: ColumnType) => {
    setEditingTask(null);
    setDefaultAddColumn(col);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (task: TaskCard) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleSaveTask = (taskData: Omit<TaskCard, 'id'> | TaskCard) => {
    if ('id' in taskData) {
      updateTask(taskData as TaskCard);
    } else {
      addTask(taskData);
    }
  };

  const totalCount = filteredTasks.length;
  const inProgressCount = filteredTasks.filter((t) => t.column === 'IN PROGRESS').length;
  const reviewCount = filteredTasks.filter((t) => t.column === 'REVIEW / TESTING').length;
  const doneCount = filteredTasks.filter((t) => t.column === 'DONE').length;

  return (
    <div className="space-y-4 pb-12">
      {/* Top Banner Stat Bar & Filter Controls matching Screen 1 */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[var(--bg-card)] p-3 border border-[var(--border-color)] rounded-lg">
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="font-bold text-[var(--text-primary)]">
            Total <span className="px-1.5 py-0.5 rounded bg-[var(--bg-card-alt)]">{totalCount}</span>
          </span>
          <span className="text-[var(--text-secondary)]">
            In Progress <span className="font-bold text-[var(--color-matcha)]">{inProgressCount}</span>
          </span>
          <span className="text-[var(--text-secondary)]">
            Review <span className="font-bold text-[var(--color-brown)]">{reviewCount}</span>
          </span>
          <span className="text-[var(--text-secondary)]">
            Done <span className="font-bold text-[var(--color-okra)]">{doneCount}</span>
          </span>
        </div>

        {/* View Switcher Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1 sm:pb-0">
          {(['Dashboard', 'Board', 'Swim Lanes', 'Due Date', 'Compact', 'List'] as const).map(
            (mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-2.5 py-1 text-xs font-mono rounded transition-colors ${
                  viewMode === mode
                    ? 'bg-[var(--text-primary)] text-[var(--bg-card)] font-bold'
                    : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {mode}
              </button>
            )
          )}
          <div className="h-4 w-px bg-[var(--border-color)] mx-1" />
          <button
            onClick={() => setCurrentView('create-project')}
            className="px-2.5 py-1 text-xs font-mono rounded btn-outline flex items-center gap-1"
          >
            <Plus className="w-3 h-3 text-[var(--color-matcha)]" /> Projects
          </button>
          <button
            onClick={() => alert('Exporting workspace data as JSON archive...')}
            className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded"
            title="Export Board Data"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={() => alert('Import workspace template...')}
            className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] rounded"
            title="Import Board Data"
          >
            <Upload className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter Category Chips matching Screen 1 */}
      <div className="flex items-center gap-2 overflow-x-auto custom-scrollbar py-1">
        <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)] shrink-0 flex items-center gap-1">
          <ListFilter className="w-3.5 h-3.5" /> FILTER:
        </span>
        {businessCategories.map((cat) => {
          const isSelected = selectedBusinessTag === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedBusinessTag(cat)}
              className={`px-3 py-1 rounded-full text-xs font-medium shrink-0 transition-all ${
                isSelected
                  ? 'bg-[var(--text-primary)] text-[var(--bg-card)] font-bold shadow-xs'
                  : 'bg-[var(--bg-card)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--text-secondary)]'
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Main Kanban Columns Container */}
      <div className="overflow-x-auto custom-scrollbar pb-4">
        <div className="flex gap-4 min-w-max">
          {columns.map((col) => {
            const columnTasks = filteredTasks.filter((t) => t.column === col.id);

            return (
              <div
                key={col.id}
                className="w-80 shrink-0 flex flex-col bg-[var(--bg-card-alt)] rounded-lg p-3 border border-[var(--border-subtle)]"
              >
                {/* Column Header */}
                <div className="flex items-center justify-between pb-3 mb-2 border-b border-[var(--border-color)]">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${col.colorClass.replace('border-t-', 'bg-')}`} />
                    <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-[var(--text-primary)]">
                      {col.title}
                    </h3>
                    <span className="text-[11px] font-mono font-bold px-1.5 py-0.2 rounded bg-[var(--bg-card)] text-[var(--text-muted)] border border-[var(--border-color)]">
                      {columnTasks.length}
                    </span>
                  </div>
                  <button
                    onClick={() => handleOpenAddModal(col.id)}
                    className="p-1 hover:bg-[var(--bg-card)] rounded text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                    title={`Add task to ${col.title}`}
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* Cards List in Column */}
                <div className="space-y-3 overflow-y-auto max-h-[calc(100vh-280px)] custom-scrollbar pr-1">
                  {columnTasks.length === 0 ? (
                    <div className="p-4 border border-dashed border-[var(--border-color)] rounded-lg text-center text-xs text-[var(--text-muted)] italic">
                      No items in {col.title}
                    </div>
                  ) : (
                    columnTasks.map((task) => (
                      <div
                        key={task.id}
                        className={`app-card p-3 shadow-xs hover:shadow-md transition-all border-t-4 ${col.colorClass} group relative`}
                      >
                        {/* Top Category Tag Badge */}
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wide bg-[var(--bg-card-alt)] text-[var(--text-primary)] border border-[var(--border-color)]">
                            {task.category}
                          </span>
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                            <button
                              onClick={() => handleOpenEditModal(task)}
                              className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                              title="Edit task"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => deleteTask(task.id)}
                              className="p-1 text-[var(--text-muted)] hover:text-[var(--color-dark-red)]"
                              title="Delete task"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>

                        {/* Task Title */}
                        <h4 className="text-xs sm:text-sm font-bold text-[var(--text-primary)] leading-tight mb-1">
                          {task.title}
                        </h4>

                        {/* Task Description */}
                        {task.description && (
                          <p className="text-xs text-[var(--text-secondary)] line-clamp-2 mb-3 leading-relaxed">
                            {task.description}
                          </p>
                        )}

                        {/* Footer Info: Priority, Due Date & Assignees */}
                        <div className="flex items-center justify-between pt-2 border-t border-[var(--border-subtle)] text-[11px] font-mono">
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${getPriorityBadgeClass(task.priority)}`}>
                              {task.priority}
                            </span>
                            {task.dueDate && (
                              <span className="flex items-center gap-1 text-[var(--color-dark-red)] font-semibold">
                                <Calendar className="w-3 h-3" />
                                {task.dueDate}
                              </span>
                            )}
                          </div>

                          {/* Quick Column Shift Buttons */}
                          <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                            {col.id !== 'IDEAS / PLANNING' && (
                              <button
                                onClick={() => {
                                  const idx = columns.findIndex((c) => c.id === col.id);
                                  const prevCol = columns[idx - 1];
                                  if (idx > 0 && prevCol) moveTaskColumn(task.id, prevCol.id);
                                }}
                                className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] bg-[var(--bg-card-alt)] rounded"
                                title="Move Left"
                              >
                                <ArrowLeft className="w-3 h-3" />
                              </button>
                            )}
                            {col.id !== 'DONE' && (
                              <button
                                onClick={() => {
                                  const idx = columns.findIndex((c) => c.id === col.id);
                                  const nextCol = columns[idx + 1];
                                  if (idx < columns.length - 1 && nextCol) moveTaskColumn(task.id, nextCol.id);
                                }}
                                className="p-1 text-[var(--text-muted)] hover:text-[var(--color-matcha)] bg-[var(--bg-card-alt)] rounded"
                                title="Move Right"
                              >
                                <ArrowRight className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Bottom Quick Add Task Button */}
                <button
                  onClick={() => handleOpenAddModal(col.id)}
                  className="mt-3 py-2 w-full border border-dashed border-[var(--border-color)] hover:border-[var(--text-secondary)] rounded-md text-xs font-mono font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors flex items-center justify-center gap-1.5"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Task
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Modal for Creating / Editing Task */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveTask}
        initialTask={editingTask}
        defaultColumn={defaultAddColumn}
      />
    </div>
  );
};
