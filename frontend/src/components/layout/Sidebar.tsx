import React from 'react';
import { useApp } from '@/context/AppContext';
import { AppView } from '@/types';
import { 
  LayoutDashboard, 
  FolderKanban, 
  KanbanSquare, 
  FlaskConical, 
  BarChart3, 
  Plus, 
  Settings, 
  HelpCircle,
  Microscope
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { currentView, setCurrentView } = useApp();

  const navItems: { id: AppView; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'projects', label: 'All Projects', icon: <FolderKanban className="w-4 h-4" /> },
    { id: 'boards', label: 'Active Boards', icon: <KanbanSquare className="w-4 h-4" /> },
    { id: 'tests', label: 'Test Suites', icon: <FlaskConical className="w-4 h-4" /> },
    { id: 'reports', label: 'Execution Reports', icon: <BarChart3 className="w-4 h-4" /> },
  ];

  return (
    <aside className="app-sidebar fixed left-0 top-16 h-[calc(100vh-64px)] w-64 flex-col z-40 hidden md:flex">
      {/* Workspace Profile Header */}
      <div className="p-4 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[var(--text-primary)] text-[var(--bg-card)] flex items-center justify-center font-bold">
            <Microscope className="w-5 h-5 text-[var(--color-matcha)]" />
          </div>
          <div>
            <h3 className="text-xs font-bold font-mono tracking-wider text-[var(--text-primary)] uppercase">
              QA Workspace
            </h3>
            <span className="inline-block text-[10px] font-mono px-1.5 py-0.2 rounded badge-matcha mt-0.5">
              v2.4.1 Stable
            </span>
          </div>
        </div>
      </div>

      {/* Main Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        {navItems.map(item => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-xs font-medium transition-all ${
                isActive
                  ? 'bg-[var(--bg-card)] text-[var(--text-primary)] font-bold border-l-4 border-[var(--color-matcha)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--bg-card-alt)] hover:text-[var(--text-primary)]'
              }`}
            >
              <span className={isActive ? 'text-[var(--color-matcha)]' : 'text-[var(--text-muted)]'}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Create New Project Call-to-action & Footer */}
      <div className="p-4 border-t border-[var(--border-color)] space-y-3">
        <button
          onClick={() => setCurrentView('create-project')}
          className="w-full py-2.5 px-3 btn-primary flex items-center justify-center gap-2 text-xs shadow-sm"
        >
          <Plus className="w-4 h-4 text-[var(--color-matcha)]" />
          <span>Create New Project</span>
        </button>

        <div className="space-y-0.5 pt-2">
          <button
            onClick={() => setCurrentView('settings')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs transition-colors ${
              currentView === 'settings' 
                ? 'text-[var(--text-primary)] font-semibold bg-[var(--bg-card)]'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)]'
            }`}
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Settings</span>
          </button>
          <button
            onClick={() => setCurrentView('reports')}
            className="w-full flex items-center gap-3 px-3 py-2 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded-md transition-colors"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Support</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
